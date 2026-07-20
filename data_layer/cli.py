#!/usr/bin/env python3
"""
CLI for service map data management.

Usage:
    python -m data_layer.cli import --data-dir data/ --db data/service_maps.db
    python -m data_layer.cli export --db data/service_maps.db --out-dir data/
    python -m data_layer.cli stats --db data/service_maps.db
    python -m data_layer.cli validate --db data/service_maps.db
    python -m data_layer.cli diff --db data/service_maps.db --data-dir data/
"""

import argparse
import json
import os
import sys

# Allow running as `python -m data_layer.cli` from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_layer import get_backend
from data_layer.models import Jurisdiction


def cmd_import(args):
    """Import JSON files into SQLite."""
    db = get_backend("sqlite", path=args.db)

    # Import jurisdictions
    jur_path = os.path.join(args.data_dir, "jurisdictions.json")
    if os.path.exists(jur_path):
        with open(jur_path) as f:
            for j_data in json.load(f):
                db.upsert_jurisdiction(Jurisdiction(
                    code=j_data["code"], name=j_data["name"],
                    short_name=j_data.get("short_name", j_data["name"]),
                    country=j_data.get("country", "CA"),
                    type=j_data["type"], parent=j_data.get("parent"),
                    path=j_data.get("path")))

    # Import taxonomy
    tax_path = os.path.join(args.data_dir, "taxonomy.json")
    if os.path.exists(tax_path):
        with open(tax_path) as f:
            db.set_taxonomy_definition(json.load(f))

    # Import each jurisdiction's data
    jurisdictions = db.list_jurisdictions()
    for j in jurisdictions:
        j_dir = os.path.join(args.data_dir, j.path or j.code)
        if os.path.isdir(j_dir):
            stats = db.import_jurisdiction_json(j.code, j_dir)
            print(f"  {j.short_name}: {stats['entities']} entities, "
                  f"{stats['supporting_services']} services, "
                  f"{stats['acts']} acts")

    total = db.stats()
    print(f"\nTotal: {total['entities']} entities, {total['supporting_services']} services "
          f"across {total['jurisdictions']} jurisdictions")
    db.close()


def cmd_export(args):
    """Export SQLite to JSON files."""
    db = get_backend("sqlite", path=args.db)
    out = args.out_dir

    # jurisdictions.json
    jur_index = db.export_jurisdictions_index()
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "jurisdictions.json"), "w") as f:
        json.dump(jur_index, f, indent=2, ensure_ascii=False)
    print(f"  jurisdictions.json ({len(jur_index)} jurisdictions)")

    # taxonomy.json
    taxonomy = db.get_taxonomy_definition()
    if taxonomy:
        with open(os.path.join(out, "taxonomy.json"), "w") as f:
            json.dump(taxonomy, f, indent=2, ensure_ascii=False)
        print("  taxonomy.json")

    # Per-jurisdiction
    for j in db.list_jurisdictions():
        j_dir = os.path.join(out, j.path or j.code)
        os.makedirs(j_dir, exist_ok=True)

        # config.json
        config = db.export_jurisdiction_config(j.code)
        with open(os.path.join(j_dir, "config.json"), "w") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # entities/ministries index
        entities = db.export_entities_index(j.code)
        # Use the same filename as the original
        index_name = "ministries.json" if j.org_unit_label == "Ministry" else "entities.json"
        with open(os.path.join(j_dir, index_name), "w") as f:
            json.dump(entities, f, indent=2, ensure_ascii=False)

        # Per-entity data files
        entity_count = 0
        leg_count = 0
        for e in db.list_entities(j.code):
            # Entity JSON
            entity_data = db.export_entity_json(e.prefix, j.code)
            with open(os.path.join(j_dir, f"{e.prefix}.json"), "w") as f:
                json.dump(entity_data, f, indent=2, ensure_ascii=False)
            entity_count += 1

            # Legislation JSON
            leg_data = db.export_legislation_json(e.prefix, j.code)
            if leg_data:
                with open(os.path.join(j_dir, f"{e.prefix}_legislation.json"), "w") as f:
                    json.dump(leg_data, f, indent=2, ensure_ascii=False)
                leg_count += 1

        print(f"  {j.short_name}: {entity_count} entities, {leg_count} legislation files")

    db.close()
    print("\nExport complete.")


def cmd_stats(args):
    """Print summary statistics."""
    db = get_backend("sqlite", path=args.db)
    s = db.stats()
    print(f"Jurisdictions:         {s['jurisdictions']}")
    print(f"Entities:              {s['entities']}")
    print(f"Goals:                 {s['goals']}")
    print(f"Main services:         {s['main_services']}")
    print(f"Supporting services:   {s['supporting_services']}")
    print(f"Foundational services: {s['foundational_services']}")
    print(f"Acts:                  {s['acts']}")
    print(f"Act sections:          {s['act_sections']}")
    print(f"Section → services:    {s['section_services']}")

    # Per-jurisdiction breakdown
    print()
    for j in db.list_jurisdictions():
        entities = db.list_entities(j.code)
        live = [e for e in entities if not e.is_test]
        ss_count = db.conn.execute("""
            SELECT COUNT(*) as c FROM supporting_services ss
            JOIN main_services ms ON ss.main_service_id = ms.id
            JOIN goals g ON ms.goal_id = g.id
            WHERE g.jurisdiction_code = ?
        """, (j.code,)).fetchone()["c"]
        print(f"  {j.short_name}: {len(live)} entities, {ss_count} services")

    db.close()


def cmd_validate(args):
    """Run integrity checks."""
    db = get_backend("sqlite", path=args.db)
    warnings = db.validate()
    if warnings:
        print(f"{len(warnings)} issues found:")
        for w in warnings[:50]:
            print(f"  - {w}")
        if len(warnings) > 50:
            print(f"  ... and {len(warnings) - 50} more")
    else:
        print("All checks passed.")
    db.close()


def cmd_diff(args):
    """Compare DB export against existing JSON files."""
    db = get_backend("sqlite", path=args.db)
    total_diffs = 0
    perfect = 0
    checked = 0

    for j in db.list_jurisdictions():
        for e in db.list_entities(j.code):
            path = os.path.join(args.data_dir, j.path or j.code, f"{e.prefix}.json")
            if not os.path.exists(path):
                continue

            exported = db.export_entity_json(e.prefix, j.code)
            with open(path) as f:
                original = json.load(f)

            diffs = 0
            for gi, (eg, og) in enumerate(
                    zip(exported.get("goals", []), original.get("goals", []))):
                for mi, (ems, oms) in enumerate(
                        zip(eg.get("main_services", []), og.get("main_services", []))):
                    exp_ss = ems.get("supporting", [])
                    orig_ss = oms.get("supporting", [])
                    if len(exp_ss) != len(orig_ss):
                        diffs += abs(len(exp_ss) - len(orig_ss))
                        continue
                    for si, (ess, oss) in enumerate(zip(exp_ss, orig_ss)):
                        for key in set(list(oss.keys()) + list(ess.keys())):
                            if json.dumps(ess.get(key), sort_keys=True) != json.dumps(oss.get(key), sort_keys=True):
                                diffs += 1

            checked += 1
            if diffs == 0:
                perfect += 1
            else:
                print(f"  {j.code}/{e.prefix}: {diffs} diffs")
            total_diffs += diffs

    print(f"\n{perfect}/{checked} entities: perfect round-trip")
    if total_diffs:
        print(f"{total_diffs} total field-level diffs")
    db.close()


def main():
    parser = argparse.ArgumentParser(description="Service map data management")
    sub = parser.add_subparsers(dest="command")

    p_import = sub.add_parser("import", help="Import JSON into SQLite")
    p_import.add_argument("--data-dir", default="data/", help="Path to data/ directory")
    p_import.add_argument("--db", default="data/service_maps.db", help="SQLite database path")

    p_export = sub.add_parser("export", help="Export SQLite to JSON")
    p_export.add_argument("--db", default="data/service_maps.db", help="SQLite database path")
    p_export.add_argument("--out-dir", default="data/", help="Output directory")

    p_stats = sub.add_parser("stats", help="Print summary statistics")
    p_stats.add_argument("--db", default="data/service_maps.db", help="SQLite database path")

    p_validate = sub.add_parser("validate", help="Run integrity checks")
    p_validate.add_argument("--db", default="data/service_maps.db", help="SQLite database path")

    p_diff = sub.add_parser("diff", help="Compare DB against JSON files")
    p_diff.add_argument("--db", default="data/service_maps.db", help="SQLite database path")
    p_diff.add_argument("--data-dir", default="data/", help="Path to data/ directory")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    {"import": cmd_import, "export": cmd_export, "stats": cmd_stats,
     "validate": cmd_validate, "diff": cmd_diff}[args.command](args)


if __name__ == "__main__":
    main()
