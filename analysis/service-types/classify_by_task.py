#!/usr/bin/env python3
"""
Phase 1: Classify every supporting service in `goa-service-maps/data/ab/` by service task.

Service task priority (driven by channels):
  Apply > Transact > Check > Engage > Find-only (informational) > Other/No-channels.

Report has no dedicated channel; we detect it by name/desc pattern. When a service has
an Apply channel but the name signals reporting (child abuse hotline, file a complaint,
etc.), we tag it as Report — Brief 06 treats Report as distinct from Apply because there
is no eligibility / assessment / decision shape.

Output:
  phase-1-classification.json  (full per-service rows + summary)
  stdout: counts by task and by ministry
"""

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Resolve paths relative to this script's location so the analysis is portable.
# Script lives in `goa-service-maps/analysis/service-types/`; data lives in `goa-service-maps/data/ab/`.
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "ab"
OUT = Path(__file__).parent / "phase-1-classification.json"

SKIP_FILES = {"ministries.json", "config.json", "taxonomy.json", "jurisdictions.json", "service_types.json"}

# Channel → task, in priority order. Apply wins over Transact wins over Check, etc.
ACTION_PRIORITY = [
    ("ch-apply", "Apply"),
    ("ch-transact", "Transact"),
    ("ch-check", "Check"),
    ("ch-engage", "Engage"),
]

# Name-pattern signals. All anchored at name start (`^`) — service names are verb-led
# per Paul's methodology, so the imperative verb at start is the strict signal.
# Matching against name only (not desc) avoids false positives from passive constructions
# like "annual reporting requirements" inside a description.

# Report: citizen pushes information (incident, complaint, concern). No eligibility
# assessment, no decision shape — that's what separates it from Apply.
REPORT_NAME = re.compile(
    r"^(report\b"
    r"|file (a|an) (complaint|grievance|concern|report|tip|incident|disclosure|human rights)"
    r"|submit (a|an) (complaint|grievance|concern|report|tip)"
    r"|make (a|an) (complaint|report|disclosure)"
    r"|lodge (a|an) (complaint|grievance)"
    r"|raise (a|an)? ?concern"
    r"|blow the whistle"
    r"|disclose\b"
    r"|whistleblow)",
    re.IGNORECASE,
)

# Apply: name starts with "Apply for/to" or "Register" — these are structurally Apply
# even when the channel is ch-transact (e.g. private investigator licence).
APPLY_NAME = re.compile(
    r"^(apply\s+(for|to)\b|register\b|enrol\b|enroll\b)",
    re.IGNORECASE,
)

# Engage: consultation/feedback verbs. ch-engage is rarely tagged in the data;
# engagement services often live across ch-email/ch-find/ch-mail.
ENGAGE_NAME = re.compile(
    r"^(have your say"
    r"|get involved"
    r"|join (a |an |the )?(consultation|public)"
    r"|participate in (a |an |the )?(consultation|public)"
    r"|submit feedback"
    r"|share your views"
    r"|comment on (a |an |the )?(proposed|public|draft)"
    r"|respond to (a |an |the )?(consultation|engagement|survey))",
    re.IGNORECASE,
)


DIGITAL_INFO_CHANNELS = {"ch-find", "ch-web", "ch-pub", "ch-pdf"}
HUMAN_MEDIATED_CHANNELS = {"ch-phone", "ch-inperson", "ch-mail", "ch-email", "ch-registry"}


def classify(channels, name, desc):
    types = {ch.get("type") for ch in (channels or []) if ch.get("type")}
    name_clean = name.strip()
    signals = {
        "name_signals_report": bool(REPORT_NAME.search(name_clean)),
        "name_signals_apply": bool(APPLY_NAME.search(name_clean)),
        "name_signals_engage": bool(ENGAGE_NAME.search(name_clean)),
    }

    # 1. Channel priority gives initial primary.
    primary = None
    for ch_type, task_label in ACTION_PRIORITY:
        if ch_type in types:
            primary = task_label
            break

    # 2. Apply name override: "Apply for X" / "Register X" is structurally Apply,
    #    even when ch-transact is the only action channel (licences, permits).
    if signals["name_signals_apply"] and primary != "Apply":
        primary = "Apply"

    # 3. Report name override: report-shaped names override any prior assignment.
    #    Critical: must run AFTER Apply override, since "File a complaint" services
    #    sometimes have ch-apply (online complaint forms) and Apply would lose them.
    if signals["name_signals_report"]:
        primary = "Report"

    # 4. Engage name override: only fires when not already Apply/Report (those are
    #    stronger signals). Catches engagement services without ch-engage.
    if signals["name_signals_engage"] and primary not in ("Apply", "Report"):
        primary = "Engage"

    # 5. Fallback for services with no action channel and no name signal.
    if primary is None:
        if not types:
            primary = "No-channels"
        elif types <= DIGITAL_INFO_CHANNELS:
            primary = "Find"  # citizen looks up info; purely informational
        elif (types & DIGITAL_INFO_CHANNELS) and (types & HUMAN_MEDIATED_CHANNELS):
            # Find/web with phone/inperson backup — citizen finds info, may call to clarify.
            primary = "Find"
        elif types <= HUMAN_MEDIATED_CHANNELS:
            # Only non-digital — citizen gets human help. No digital action surface.
            primary = "Advise"
        else:
            primary = "Unclassified"

    return primary, sorted(types), signals


def walk(prefix, data):
    rows = []
    ministry_name = data.get("short_name") or data.get("full_name") or prefix
    for goal in data.get("goals", []):
        goal_num = goal.get("number")
        goal_name = goal.get("short_name") or goal.get("legend_label") or goal.get("title")
        for ms in goal.get("main_services", []):
            ms_num = ms.get("number")
            ms_name = ms.get("name")
            for sup in ms.get("supporting", []):
                name = sup.get("name", "")
                desc = sup.get("desc", "")
                channels = sup.get("channels", [])
                task, channel_types, signals = classify(channels, name, desc)
                tax = sup.get("taxonomy") or {}
                rows.append({
                    "ministry_prefix": prefix,
                    "ministry_name": ministry_name,
                    "goal_number": goal_num,
                    "goal_name": goal_name,
                    "main_service_number": ms_num,
                    "main_service_name": ms_name,
                    "name": name,
                    "desc": desc,
                    "users": sup.get("users", ""),
                    "user_groups": sup.get("user_groups", []),
                    "channels": channel_types,
                    "primary_task": task,
                    "signals": signals,
                    "track": tax.get("track"),
                    "tier": tax.get("tier"),
                    "domain": tax.get("domain"),
                    "relationships": tax.get("relationships", []),
                    "legislation": [
                        l.get("abbrev")
                        for l in (sup.get("legislation") or [])
                        if l.get("abbrev")
                    ],
                    "mandate_tags": [
                        (t.get("number") if isinstance(t, dict) else t)
                        for t in (sup.get("mandate_tags") or [])
                        if (isinstance(t, dict) and t.get("number") is not None)
                        or (isinstance(t, str) and t)
                    ],
                    "deep_dive": sup.get("deep_dive"),
                })
    return rows


def main():
    all_rows = []
    loaded = []
    for f in sorted(DATA_DIR.glob("*.json")):
        if f.name in SKIP_FILES:
            continue
        if f.name.endswith("_legislation.json") or f.name.endswith("_dia.json"):
            continue
        with f.open() as fp:
            data = json.load(fp)
        prefix = data.get("prefix") or f.stem
        rows = walk(prefix, data)
        all_rows.extend(rows)
        loaded.append((prefix, len(rows)))

    by_task = Counter(r["primary_task"] for r in all_rows)
    by_task_ministries = defaultdict(set)
    for r in all_rows:
        by_task_ministries[r["primary_task"]].add(r["ministry_prefix"])

    print(f"Ministries loaded: {len(loaded)}")
    print(f"Total supporting services: {len(all_rows)}")
    print()
    print("Services per ministry:")
    for prefix, n in sorted(loaded):
        print(f"  {prefix:8s} {n:4d}")
    print()
    print("Primary task counts:")
    for task, n in by_task.most_common():
        m = len(by_task_ministries[task])
        print(f"  {task:14s} {n:4d}  ({m} ministries)")

    with OUT.open("w") as fp:
        json.dump({
            "summary": {
                "ministries_loaded": [
                    {"prefix": p, "service_count": n} for p, n in loaded
                ],
                "total_supporting_services": len(all_rows),
                "by_primary_task": dict(by_task),
                "task_ministry_spread": {
                    task: sorted(prefixes)
                    for task, prefixes in by_task_ministries.items()
                },
            },
            "services": all_rows,
        }, fp, indent=2)
    print()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
