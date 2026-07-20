"""
SQLite implementation of the DataBackend interface.
"""

from __future__ import annotations
import json
import os
import sqlite3
from typing import Optional

from data_layer.interface import DataBackend
from data_layer.models import (
    Jurisdiction, Entity, Goal, MainService,
    SupportingService, FoundationalService,
    Channel, LegislationRef, Taxonomy, Relationship,
    Act, ActSection, SectionService,
)


class SQLiteBackend(DataBackend):

    def __init__(self, path: str = "data/service_maps.db"):
        self.path = path
        self.conn: Optional[sqlite3.Connection] = None
        self._connect()
        self.initialize()

    def _connect(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    # ── Schema ────────────────────────────────────────────────

    def initialize(self):
        c = self.conn
        c.executescript("""
        CREATE TABLE IF NOT EXISTS jurisdictions (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            short_name TEXT NOT NULL,
            country TEXT NOT NULL DEFAULT 'CA',
            type TEXT NOT NULL,
            parent TEXT,
            path TEXT,
            brand_color TEXT DEFAULT '#00405c',
            brand_color_light TEXT,
            accent_color TEXT,
            org_unit_label TEXT DEFAULT 'Ministry',
            goal_label TEXT DEFAULT 'Outcome',
            main_service_label TEXT DEFAULT 'Main Service',
            last_updated TEXT,
            legislation_source TEXT,
            mandate_source_type TEXT,
            channel_types_json TEXT DEFAULT '{}',
            reach_tiers_json TEXT,
            impact_categories_json TEXT,
            FOREIGN KEY (parent) REFERENCES jurisdictions(code)
        );

        CREATE TABLE IF NOT EXISTS entities (
            prefix TEXT NOT NULL,
            jurisdiction_code TEXT NOT NULL,
            name TEXT NOT NULL,
            short_name TEXT NOT NULL,
            blurb TEXT,
            nav_name TEXT,
            has_registry_agents INTEGER DEFAULT 0,
            is_test INTEGER DEFAULT 0,
            mandate_date TEXT,
            mandate_minister TEXT,
            mandate_pdf TEXT,
            cross_cutting_json TEXT DEFAULT '[]',
            mandate_legend_json TEXT DEFAULT '[]',
            PRIMARY KEY (prefix, jurisdiction_code),
            FOREIGN KEY (jurisdiction_code) REFERENCES jurisdictions(code)
        );

        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_prefix TEXT NOT NULL,
            jurisdiction_code TEXT NOT NULL,
            number INTEGER NOT NULL,
            color TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL DEFAULT '',
            short_name TEXT NOT NULL DEFAULT '',
            legend_label TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            UNIQUE (entity_prefix, jurisdiction_code, number),
            FOREIGN KEY (entity_prefix, jurisdiction_code) REFERENCES entities(prefix, jurisdiction_code)
        );

        CREATE TABLE IF NOT EXISTS main_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_id INTEGER NOT NULL,
            number INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            UNIQUE (goal_id, number),
            FOREIGN KEY (goal_id) REFERENCES goals(id)
        );

        CREATE TABLE IF NOT EXISTS supporting_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_service_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            desc_text TEXT,
            users TEXT,
            user_groups_json TEXT DEFAULT '[]',
            channels_json TEXT DEFAULT '[]',
            legislation_json TEXT DEFAULT '[]',
            mandate_tags_json TEXT DEFAULT '[]',
            taxonomy_json TEXT,
            extra_json TEXT DEFAULT '{}',
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (main_service_id) REFERENCES main_services(id)
        );

        CREATE TABLE IF NOT EXISTS foundational_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_type TEXT NOT NULL,       -- 'entity', 'goal', 'main_service'
            parent_entity_prefix TEXT,       -- for entity-level
            parent_jurisdiction_code TEXT,   -- for entity-level
            parent_goal_id INTEGER,          -- for goal-level
            parent_ms_id INTEGER,            -- for main_service-level
            is_string INTEGER DEFAULT 0,
            string_value TEXT,
            source_id TEXT,                  -- original "id" field like "f-6"
            name TEXT DEFAULT '',
            desc_text TEXT,
            users TEXT,
            user_groups_json TEXT DEFAULT '[]',
            channels_json TEXT DEFAULT '[]',
            legislation_json TEXT DEFAULT '[]',
            mandate_tags_json TEXT DEFAULT '[]',
            taxonomy_json TEXT,
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (parent_goal_id) REFERENCES goals(id),
            FOREIGN KEY (parent_ms_id) REFERENCES main_services(id)
        );

        CREATE TABLE IF NOT EXISTS acts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_prefix TEXT NOT NULL,
            jurisdiction_code TEXT NOT NULL,
            abbrev TEXT NOT NULL,
            full_name TEXT NOT NULL DEFAULT '',
            color TEXT NOT NULL DEFAULT '',
            citation TEXT,
            summary TEXT,
            full_text TEXT,
            sort_order INTEGER DEFAULT 0,
            UNIQUE (entity_prefix, jurisdiction_code, abbrev),
            FOREIGN KEY (entity_prefix, jurisdiction_code) REFERENCES entities(prefix, jurisdiction_code)
        );

        CREATE TABLE IF NOT EXISTS act_sections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            act_id INTEGER NOT NULL,
            ref TEXT NOT NULL DEFAULT '',
            title TEXT NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            anchor_id TEXT NOT NULL DEFAULT '',
            sort_order INTEGER DEFAULT 0,
            FOREIGN KEY (act_id) REFERENCES acts(id)
        );

        CREATE TABLE IF NOT EXISTS section_services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL,
            service_name TEXT NOT NULL,
            service_type TEXT NOT NULL DEFAULT 'supporting',
            goal_number INTEGER,
            goal_color TEXT DEFAULT '',
            ms_number INTEGER,
            ms_name TEXT DEFAULT '',
            FOREIGN KEY (section_id) REFERENCES act_sections(id)
        );

        CREATE TABLE IF NOT EXISTS taxonomy_definition (
            id INTEGER PRIMARY KEY DEFAULT 1,
            definition_json TEXT NOT NULL
        );
        """)
        c.commit()

    # ── Jurisdictions ─────────────────────────────────────────

    def upsert_jurisdiction(self, j: Jurisdiction):
        self.conn.execute("""
            INSERT INTO jurisdictions (code, name, short_name, country, type, parent, path,
                brand_color, brand_color_light, accent_color,
                org_unit_label, goal_label, main_service_label,
                last_updated, legislation_source, mandate_source_type,
                channel_types_json, reach_tiers_json, impact_categories_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(code) DO UPDATE SET
                name=excluded.name, short_name=excluded.short_name,
                country=excluded.country, type=excluded.type, parent=excluded.parent,
                path=excluded.path,
                brand_color=excluded.brand_color, brand_color_light=excluded.brand_color_light,
                accent_color=excluded.accent_color,
                org_unit_label=excluded.org_unit_label, goal_label=excluded.goal_label,
                main_service_label=excluded.main_service_label,
                last_updated=excluded.last_updated, legislation_source=excluded.legislation_source,
                mandate_source_type=excluded.mandate_source_type,
                channel_types_json=excluded.channel_types_json,
                reach_tiers_json=excluded.reach_tiers_json,
                impact_categories_json=excluded.impact_categories_json
        """, (j.code, j.name, j.short_name, j.country, j.type, j.parent, j.path,
              j.brand_color, j.brand_color_light, j.accent_color,
              j.org_unit_label, j.goal_label, j.main_service_label,
              j.last_updated, j.legislation_source, j.mandate_source_type,
              json.dumps(j.channel_types), _opt_json(j.reach_tiers), _opt_json(j.impact_categories)))
        self.conn.commit()

    def get_jurisdiction(self, code: str) -> Optional[Jurisdiction]:
        row = self.conn.execute("SELECT * FROM jurisdictions WHERE code=?", (code,)).fetchone()
        return _row_to_jurisdiction(row) if row else None

    def list_jurisdictions(self) -> list[Jurisdiction]:
        rows = self.conn.execute("SELECT * FROM jurisdictions ORDER BY code").fetchall()
        return [_row_to_jurisdiction(r) for r in rows]

    # ── Entities ──────────────────────────────────────────────

    def upsert_entity(self, e: Entity):
        self.conn.execute("""
            INSERT INTO entities (prefix, jurisdiction_code, name, short_name, blurb, nav_name,
                has_registry_agents, is_test, mandate_date, mandate_minister, mandate_pdf,
                cross_cutting_json, mandate_legend_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(prefix, jurisdiction_code) DO UPDATE SET
                name=excluded.name, short_name=excluded.short_name, blurb=excluded.blurb,
                nav_name=excluded.nav_name, has_registry_agents=excluded.has_registry_agents,
                is_test=excluded.is_test, mandate_date=excluded.mandate_date,
                mandate_minister=excluded.mandate_minister, mandate_pdf=excluded.mandate_pdf,
                cross_cutting_json=excluded.cross_cutting_json,
                mandate_legend_json=excluded.mandate_legend_json
        """, (e.prefix, e.jurisdiction_code, e.name, e.short_name, e.blurb, e.nav_name,
              int(e.has_registry_agents), int(e.is_test),
              e.mandate_date, e.mandate_minister, e.mandate_pdf,
              json.dumps(e.cross_cutting), json.dumps(e.mandate_legend)))
        self.conn.commit()

    def get_entity(self, prefix: str, jurisdiction_code: str) -> Optional[Entity]:
        row = self.conn.execute(
            "SELECT * FROM entities WHERE prefix=? AND jurisdiction_code=?",
            (prefix, jurisdiction_code)).fetchone()
        return _row_to_entity(row) if row else None

    def list_entities(self, jurisdiction_code: str) -> list[Entity]:
        rows = self.conn.execute(
            "SELECT * FROM entities WHERE jurisdiction_code=? ORDER BY prefix",
            (jurisdiction_code,)).fetchall()
        return [_row_to_entity(r) for r in rows]

    # ── Goals ─────────────────────────────────────────────────

    def upsert_goal(self, g: Goal) -> int:
        self.conn.execute("""
            INSERT INTO goals (entity_prefix, jurisdiction_code, number, color, title,
                short_name, legend_label, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_prefix, jurisdiction_code, number) DO UPDATE SET
                color=excluded.color, title=excluded.title,
                short_name=excluded.short_name, legend_label=excluded.legend_label,
                description=excluded.description
        """, (g.entity_prefix, g.jurisdiction_code, g.number, g.color, g.title,
              g.short_name, g.legend_label, g.description))
        self.conn.commit()
        row = self.conn.execute(
            "SELECT id FROM goals WHERE entity_prefix=? AND jurisdiction_code=? AND number=?",
            (g.entity_prefix, g.jurisdiction_code, g.number)).fetchone()
        return row["id"]

    def list_goals(self, entity_prefix: str, jurisdiction_code: str) -> list[Goal]:
        rows = self.conn.execute(
            "SELECT * FROM goals WHERE entity_prefix=? AND jurisdiction_code=? ORDER BY number",
            (entity_prefix, jurisdiction_code)).fetchall()
        return [_row_to_goal(r) for r in rows]

    # ── Main Services ─────────────────────────────────────────

    def upsert_main_service(self, ms: MainService) -> int:
        self.conn.execute("""
            INSERT INTO main_services (goal_id, number, name)
            VALUES (?, ?, ?)
            ON CONFLICT(goal_id, number) DO UPDATE SET name=excluded.name
        """, (ms.goal_id, ms.number, ms.name))
        self.conn.commit()
        row = self.conn.execute(
            "SELECT id FROM main_services WHERE goal_id=? AND number=?",
            (ms.goal_id, ms.number)).fetchone()
        return row["id"]

    def list_main_services(self, goal_id: int) -> list[MainService]:
        rows = self.conn.execute(
            "SELECT * FROM main_services WHERE goal_id=? ORDER BY number",
            (goal_id,)).fetchall()
        return [MainService(id=r["id"], goal_id=r["goal_id"], number=r["number"], name=r["name"])
                for r in rows]

    # ── Supporting Services ───────────────────────────────────

    def upsert_supporting_service(self, ss: SupportingService) -> int:
        cur = self.conn.execute("""
            INSERT INTO supporting_services (main_service_id, name, desc_text, users,
                user_groups_json, channels_json, legislation_json, mandate_tags_json,
                taxonomy_json, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (ss.main_service_id, ss.name, ss.desc, ss.users,
              json.dumps(ss.user_groups),
              json.dumps([_channel_to_dict(c) for c in ss.channels]),
              json.dumps([_legref_to_dict(l) for l in ss.legislation]),
              json.dumps(ss.mandate_tags),
              _taxonomy_to_json(ss.taxonomy),
              ss.id or 0))  # use id as sort_order hint if provided
        self.conn.commit()
        return cur.lastrowid

    def list_supporting_services(self, main_service_id: int) -> list[SupportingService]:
        rows = self.conn.execute(
            "SELECT * FROM supporting_services WHERE main_service_id=? ORDER BY sort_order, id",
            (main_service_id,)).fetchall()
        return [_row_to_supporting(r) for r in rows]

    # ── Foundational Services ─────────────────────────────────

    def upsert_foundational_service(self, fs: FoundationalService) -> int:
        cur = self.conn.execute("""
            INSERT INTO foundational_services (parent_type,
                parent_entity_prefix, parent_jurisdiction_code,
                parent_goal_id, parent_ms_id,
                is_string, string_value, source_id,
                name, desc_text, users,
                user_groups_json, channels_json, legislation_json,
                mandate_tags_json, taxonomy_json, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fs.parent_type,
              fs.parent_id if fs.parent_type == "entity" else None,  # entity prefix
              None,  # jurisdiction — set below
              fs.parent_id if fs.parent_type == "goal" else None,
              fs.parent_id if fs.parent_type == "main_service" else None,
              int(fs.is_string), fs.string_value, fs.source_id,
              fs.name, fs.desc, fs.users,
              json.dumps(fs.user_groups),
              json.dumps([_channel_to_dict(c) for c in fs.channels]),
              json.dumps([_legref_to_dict(l) for l in fs.legislation]),
              json.dumps(fs.mandate_tags),
              _taxonomy_to_json(fs.taxonomy),
              0))
        self.conn.commit()
        return cur.lastrowid

    def list_foundational_services(self, parent_type: str, parent_id: int) -> list[FoundationalService]:
        if parent_type == "entity":
            # parent_id here is actually entity_prefix — need special handling
            # This is called differently; see _load_foundational_for_entity
            raise NotImplementedError("Use _list_foundational_for_entity instead")
        col = "parent_goal_id" if parent_type == "goal" else "parent_ms_id"
        rows = self.conn.execute(
            f"SELECT * FROM foundational_services WHERE parent_type=? AND {col}=? ORDER BY sort_order, id",
            (parent_type, parent_id)).fetchall()
        return [_row_to_foundational(r) for r in rows]

    def _list_foundational_for_entity(self, prefix: str, jurisdiction_code: str) -> list[FoundationalService]:
        rows = self.conn.execute(
            """SELECT * FROM foundational_services
               WHERE parent_type='entity' AND parent_entity_prefix=? AND parent_jurisdiction_code=?
               ORDER BY sort_order, id""",
            (prefix, jurisdiction_code)).fetchall()
        return [_row_to_foundational(r) for r in rows]

    def _insert_foundational(self, fs_data, parent_type, parent_id, jurisdiction_code=None, entity_prefix=None, sort_order=0):
        """Internal helper for importing foundational services."""
        if isinstance(fs_data, str):
            self.conn.execute("""
                INSERT INTO foundational_services (parent_type,
                    parent_entity_prefix, parent_jurisdiction_code,
                    parent_goal_id, parent_ms_id,
                    is_string, string_value, sort_order)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (parent_type,
                  entity_prefix if parent_type == "entity" else None,
                  jurisdiction_code if parent_type == "entity" else None,
                  parent_id if parent_type == "goal" else None,
                  parent_id if parent_type == "main_service" else None,
                  fs_data, sort_order))
            return

        self.conn.execute("""
            INSERT INTO foundational_services (parent_type,
                parent_entity_prefix, parent_jurisdiction_code,
                parent_goal_id, parent_ms_id,
                is_string, source_id, name, desc_text, users,
                user_groups_json, channels_json, legislation_json,
                mandate_tags_json, taxonomy_json, sort_order)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (parent_type,
              entity_prefix if parent_type == "entity" else None,
              jurisdiction_code if parent_type == "entity" else None,
              parent_id if parent_type == "goal" else None,
              parent_id if parent_type == "main_service" else None,
              fs_data.get("id"), fs_data.get("name", ""), fs_data.get("desc"),
              fs_data.get("users"),
              json.dumps(fs_data.get("user_groups", [])),
              json.dumps(fs_data.get("channels", [])),
              json.dumps(fs_data.get("legislation", [])),
              json.dumps(fs_data.get("mandate_tags", [])),
              json.dumps(fs_data.get("taxonomy")) if fs_data.get("taxonomy") else None,
              sort_order))

    # ── Acts / Legislation ────────────────────────────────────

    def upsert_act(self, act: Act) -> int:
        self.conn.execute("""
            INSERT INTO acts (entity_prefix, jurisdiction_code, abbrev, full_name, color,
                citation, summary, full_text, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(entity_prefix, jurisdiction_code, abbrev) DO UPDATE SET
                full_name=excluded.full_name, color=excluded.color,
                citation=excluded.citation, summary=excluded.summary,
                full_text=excluded.full_text, sort_order=excluded.sort_order
        """, (act.entity_prefix, act.jurisdiction_code, act.abbrev, act.full_name,
              act.color, act.citation, act.summary, act.full_text, act.sort_order or 0))
        self.conn.commit()
        row = self.conn.execute(
            "SELECT id FROM acts WHERE entity_prefix=? AND jurisdiction_code=? AND abbrev=?",
            (act.entity_prefix, act.jurisdiction_code, act.abbrev)).fetchone()
        return row["id"]

    def list_acts(self, entity_prefix: str, jurisdiction_code: str) -> list[Act]:
        rows = self.conn.execute(
            "SELECT * FROM acts WHERE entity_prefix=? AND jurisdiction_code=? ORDER BY sort_order, id",
            (entity_prefix, jurisdiction_code)).fetchall()
        return [_row_to_act(r) for r in rows]

    def upsert_act_section(self, section: ActSection) -> int:
        cur = self.conn.execute("""
            INSERT INTO act_sections (act_id, ref, title, description, anchor_id, sort_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (section.act_id, section.ref, section.title, section.description,
              section.anchor_id, section.sort_order or 0))
        self.conn.commit()
        return cur.lastrowid

    def list_act_sections(self, act_id: int) -> list[ActSection]:
        rows = self.conn.execute(
            "SELECT * FROM act_sections WHERE act_id=? ORDER BY sort_order, id",
            (act_id,)).fetchall()
        return [ActSection(id=r["id"], act_id=r["act_id"], ref=r["ref"], title=r["title"],
                           description=r["description"], anchor_id=r["anchor_id"])
                for r in rows]

    def upsert_section_service(self, ss: SectionService):
        self.conn.execute("""
            INSERT INTO section_services (section_id, service_name, service_type,
                goal_number, goal_color, ms_number, ms_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ss.section_id, ss.service_name, ss.service_type,
              ss.goal_number, ss.goal_color, ss.ms_number, ss.ms_name))
        self.conn.commit()

    def list_section_services(self, section_id: int) -> list[SectionService]:
        rows = self.conn.execute(
            "SELECT * FROM section_services WHERE section_id=? ORDER BY id",
            (section_id,)).fetchall()
        return [SectionService(section_id=r["section_id"], service_name=r["service_name"],
                               service_type=r["service_type"], goal_number=r["goal_number"],
                               goal_color=r["goal_color"], ms_number=r["ms_number"],
                               ms_name=r["ms_name"])
                for r in rows]

    # ── Taxonomy Definition ───────────────────────────────────

    def set_taxonomy_definition(self, taxonomy_json: dict):
        self.conn.execute("""
            INSERT INTO taxonomy_definition (id, definition_json) VALUES (1, ?)
            ON CONFLICT(id) DO UPDATE SET definition_json=excluded.definition_json
        """, (json.dumps(taxonomy_json),))
        self.conn.commit()

    def get_taxonomy_definition(self) -> dict:
        row = self.conn.execute("SELECT definition_json FROM taxonomy_definition WHERE id=1").fetchone()
        return json.loads(row["definition_json"]) if row else {}

    # ── Import ────────────────────────────────────────────────

    def import_jurisdiction_json(self, jurisdiction_code: str, data_dir: str) -> dict:
        """Import all JSON for a jurisdiction. data_dir is the jurisdiction's data folder."""
        stats = {"entities": 0, "goals": 0, "main_services": 0,
                 "supporting_services": 0, "foundational_services": 0,
                 "acts": 0, "sections": 0, "section_services": 0}

        # Load config
        config_path = os.path.join(data_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = json.load(f)
            j = self.get_jurisdiction(jurisdiction_code)
            if j:
                j.brand_color = config.get("brand_color", j.brand_color)
                j.brand_color_light = config.get("brand_color_light")
                j.accent_color = config.get("accent_color")
                j.org_unit_label = config.get("org_unit_label", j.org_unit_label)
                j.goal_label = config.get("goal_label", j.goal_label)
                j.main_service_label = config.get("main_service_label", j.main_service_label)
                j.last_updated = config.get("last_updated")
                j.legislation_source = config.get("legislation_source")
                j.mandate_source_type = config.get("mandate_source_type")
                j.channel_types = config.get("channel_types", {})
                j.reach_tiers = config.get("reach_tiers")
                j.impact_categories = config.get("impact_categories")
                self.upsert_jurisdiction(j)

        # Load entity index
        entities_data = []
        for index_file in ["entities.json", "ministries.json"]:
            path = os.path.join(data_dir, index_file)
            if os.path.exists(path):
                with open(path) as f:
                    entities_data = json.load(f)
                break

        # Import each entity
        for e_data in entities_data:
            prefix = e_data["prefix"]
            entity = Entity(
                prefix=prefix,
                jurisdiction_code=jurisdiction_code,
                name=e_data.get("name", ""),
                short_name=e_data.get("short_name", e_data.get("name", "")),
                blurb=e_data.get("blurb"),
                is_test=e_data.get("is_test", False),
            )

            # Load full entity data
            entity_path = os.path.join(data_dir, f"{prefix}.json")
            if os.path.exists(entity_path):
                with open(entity_path) as f:
                    full = json.load(f)
                entity.nav_name = full.get("nav_name")
                entity.has_registry_agents = full.get("has_registry_agents", False)
                entity.mandate_date = full.get("mandate_date")
                entity.mandate_minister = full.get("mandate_minister")
                entity.mandate_pdf = full.get("mandate_pdf")
                entity.cross_cutting = full.get("cross_cutting", [])
                entity.mandate_legend = full.get("mandate_legend", [])

                self.upsert_entity(entity)
                stats["entities"] += 1

                # Foundational services at entity level
                for i, fs in enumerate(full.get("foundational_services", [])):
                    self._insert_foundational(fs, "entity", None,
                                              jurisdiction_code=jurisdiction_code,
                                              entity_prefix=prefix, sort_order=i)
                    stats["foundational_services"] += 1

                # Goals
                for g_data in full.get("goals", []):
                    goal = Goal(
                        entity_prefix=prefix, jurisdiction_code=jurisdiction_code,
                        number=g_data["number"], color=g_data.get("color", ""),
                        title=g_data.get("title", ""), short_name=g_data.get("short_name", ""),
                        legend_label=g_data.get("legend_label", ""),
                        description=g_data.get("description", ""))
                    goal_id = self.upsert_goal(goal)
                    stats["goals"] += 1

                    # Goal-level foundational
                    for i, fs in enumerate(g_data.get("foundational_services", [])):
                        self._insert_foundational(fs, "goal", goal_id, sort_order=i)
                        stats["foundational_services"] += 1

                    # Main services
                    for ms_data in g_data.get("main_services", []):
                        ms = MainService(goal_id=goal_id, number=ms_data["number"],
                                         name=ms_data.get("name", ""))
                        ms_id = self.upsert_main_service(ms)
                        stats["main_services"] += 1

                        # MS-level foundational
                        for i, fs in enumerate(ms_data.get("foundational_services", [])):
                            self._insert_foundational(fs, "main_service", ms_id, sort_order=i)
                            stats["foundational_services"] += 1

                        # Supporting services
                        _known_ss_keys = {"name", "desc", "users", "user_groups", "channels",
                                          "legislation", "mandate_tags", "taxonomy"}
                        for i, ss_data in enumerate(ms_data.get("supporting", [])):
                            extra = {k: v for k, v in ss_data.items() if k not in _known_ss_keys}
                            self.conn.execute("""
                                INSERT INTO supporting_services (main_service_id, name, desc_text,
                                    users, user_groups_json, channels_json, legislation_json,
                                    mandate_tags_json, taxonomy_json, extra_json, sort_order)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (ms_id, ss_data.get("name", ""), ss_data.get("desc"),
                                  ss_data.get("users"),
                                  json.dumps(ss_data.get("user_groups", [])),
                                  json.dumps(ss_data.get("channels", [])),
                                  json.dumps(ss_data.get("legislation", [])),
                                  json.dumps(ss_data.get("mandate_tags", [])),
                                  json.dumps(ss_data.get("taxonomy")) if ss_data.get("taxonomy") else None,
                                  json.dumps(extra) if extra else "{}",
                                  i))
                            stats["supporting_services"] += 1

            else:
                self.upsert_entity(entity)
                stats["entities"] += 1

            # Legislation
            leg_path = os.path.join(data_dir, f"{prefix}_legislation.json")
            if os.path.exists(leg_path):
                with open(leg_path) as f:
                    leg = json.load(f)
                for i, act_data in enumerate(leg.get("acts", [])):
                    act = Act(
                        entity_prefix=prefix, jurisdiction_code=jurisdiction_code,
                        abbrev=act_data["abbrev"], full_name=act_data.get("full_name", ""),
                        color=act_data.get("color", ""), citation=act_data.get("citation"),
                        summary=act_data.get("summary"), full_text=act_data.get("full_text"),
                        sort_order=i)
                    act_id = self.upsert_act(act)
                    stats["acts"] += 1

                    for j, sec_data in enumerate(act_data.get("sections", [])):
                        sec = ActSection(
                            act_id=act_id, ref=sec_data.get("ref", ""),
                            title=sec_data.get("title", ""),
                            description=sec_data.get("description", ""),
                            anchor_id=sec_data.get("anchor_id", ""),
                            sort_order=j)
                        sec_id = self.upsert_act_section(sec)
                        stats["sections"] += 1

                        for svc_data in sec_data.get("services", []):
                            ss = SectionService(
                                section_id=sec_id,
                                service_name=svc_data.get("name", ""),
                                service_type=svc_data.get("type", "supporting"),
                                goal_number=svc_data.get("goal_number"),
                                goal_color=svc_data.get("goal_color", ""),
                                ms_number=svc_data.get("ms_number"),
                                ms_name=svc_data.get("ms_name", ""))
                            self.upsert_section_service(ss)
                            stats["section_services"] += 1

        self.conn.commit()
        return stats

    # ── Export ─────────────────────────────────────────────────

    def export_entity_json(self, entity_prefix: str, jurisdiction_code: str) -> dict:
        entity = self.get_entity(entity_prefix, jurisdiction_code)
        if not entity:
            raise ValueError(f"Entity {entity_prefix} not found in {jurisdiction_code}")

        jur = self.get_jurisdiction(jurisdiction_code)
        result = {
            "prefix": entity.prefix,
            "full_name": entity.name,
            "short_name": entity.short_name,
            "blurb": entity.blurb or "",
            "nav_name": entity.nav_name or entity.short_name,
            "has_registry_agents": entity.has_registry_agents,
        }

        # Optional mandate fields
        if entity.mandate_date:
            result["mandate_date"] = entity.mandate_date
        if entity.mandate_minister:
            result["mandate_minister"] = entity.mandate_minister
        if entity.mandate_pdf:
            result["mandate_pdf"] = entity.mandate_pdf
        if entity.cross_cutting:
            result["cross_cutting"] = entity.cross_cutting
        if entity.mandate_legend:
            result["mandate_legend"] = entity.mandate_legend

        # Entity-level foundational services
        fs_rows = self.conn.execute(
            """SELECT * FROM foundational_services
               WHERE parent_type='entity' AND parent_entity_prefix=? AND parent_jurisdiction_code=?
               ORDER BY sort_order, id""",
            (entity_prefix, jurisdiction_code)).fetchall()
        if fs_rows:
            result["foundational_services"] = [_export_foundational(r) for r in fs_rows]

        # Goals
        goals = []
        for g_row in self.conn.execute(
            "SELECT * FROM goals WHERE entity_prefix=? AND jurisdiction_code=? ORDER BY number",
            (entity_prefix, jurisdiction_code)).fetchall():

            goal_dict = {
                "number": g_row["number"],
                "color": g_row["color"],
                "title": g_row["title"],
                "short_name": g_row["short_name"],
                "legend_label": g_row["legend_label"],
                "description": g_row["description"],
            }

            # Goal-level foundational
            gfs_rows = self.conn.execute(
                "SELECT * FROM foundational_services WHERE parent_type='goal' AND parent_goal_id=? ORDER BY sort_order, id",
                (g_row["id"],)).fetchall()
            if gfs_rows:
                goal_dict["foundational_services"] = [_export_foundational(r) for r in gfs_rows]

            # Main services
            main_services = []
            for ms_row in self.conn.execute(
                "SELECT * FROM main_services WHERE goal_id=? ORDER BY number",
                (g_row["id"],)).fetchall():

                ms_dict = {"number": ms_row["number"], "name": ms_row["name"]}

                # MS-level foundational
                msfs_rows = self.conn.execute(
                    "SELECT * FROM foundational_services WHERE parent_type='main_service' AND parent_ms_id=? ORDER BY sort_order, id",
                    (ms_row["id"],)).fetchall()
                if msfs_rows:
                    ms_dict["foundational_services"] = [_export_foundational(r) for r in msfs_rows]

                # Supporting services
                supporting = []
                for ss_row in self.conn.execute(
                    "SELECT * FROM supporting_services WHERE main_service_id=? ORDER BY sort_order, id",
                    (ms_row["id"],)).fetchall():
                    supporting.append(_export_supporting(ss_row))
                ms_dict["supporting"] = supporting

                main_services.append(ms_dict)
            goal_dict["main_services"] = main_services
            goals.append(goal_dict)

        result["goals"] = goals

        # Computed fields — channel_filters, user_group_filters, channel_types, digital_channels
        result.update(self._compute_filters(entity_prefix, jurisdiction_code))

        return result

    def export_legislation_json(self, entity_prefix: str, jurisdiction_code: str) -> Optional[dict]:
        entity = self.get_entity(entity_prefix, jurisdiction_code)
        if not entity:
            return None

        acts = self.list_acts(entity_prefix, jurisdiction_code)
        if not acts:
            return None

        goals = self.list_goals(entity_prefix, jurisdiction_code)

        result = {
            "prefix": entity_prefix,
            "name": entity.name,
            "short_name": entity.short_name,
        }

        # Simplified goals for legislation page
        goals_list = []
        for g in goals:
            g_dict = {"number": g.number, "color": g.color, "short_name": g.short_name,
                      "legend_label": g.legend_label}
            ms_list = []
            for ms in self.list_main_services(g.id):
                ms_list.append({"number": ms.number, "name": ms.name})
            g_dict["main_services"] = ms_list
            goals_list.append(g_dict)
        result["goals"] = goals_list

        # Acts
        acts_list = []
        services_with_leg = set()
        multi_act_services = {}

        for act in acts:
            act_dict = {
                "abbrev": act.abbrev,
                "full_name": act.full_name,
                "color": act.color,
            }
            if act.citation:
                act_dict["citation"] = act.citation
            if act.summary:
                act_dict["summary"] = act.summary
            if act.full_text:
                act_dict["full_text"] = act.full_text

            sections = self.list_act_sections(act.id)
            sec_list = []
            for sec in sections:
                sec_dict = {
                    "ref": sec.ref,
                    "title": sec.title,
                    "description": sec.description,
                    "anchor_id": sec.anchor_id,
                }
                svcs = self.list_section_services(sec.id)
                svc_list = []
                for svc in svcs:
                    svc_dict = {
                        "type": svc.service_type,
                        "name": svc.service_name,
                        "goal_number": svc.goal_number,
                        "goal_color": svc.goal_color,
                        "ms_number": svc.ms_number,
                        "ms_name": svc.ms_name,
                    }
                    svc_list.append(svc_dict)
                    services_with_leg.add(svc.service_name)
                    multi_act_services.setdefault(svc.service_name, set()).add(act.abbrev)
                sec_dict["services"] = svc_list
                sec_list.append(sec_dict)

            act_dict["sections"] = sec_list
            acts_list.append(act_dict)

        result["acts"] = acts_list

        # Stats
        total_sections = sum(len(self.list_act_sections(a.id)) for a in acts)
        multi_count = sum(1 for s, aa in multi_act_services.items() if len(aa) > 1)
        result["stats"] = {
            "acts_count": len(acts),
            "sections_count": total_sections,
            "services_with_leg_count": len(services_with_leg),
            "services_multi_act_count": multi_count,
        }

        return result

    def export_jurisdiction_config(self, jurisdiction_code: str) -> dict:
        j = self.get_jurisdiction(jurisdiction_code)
        if not j:
            raise ValueError(f"Jurisdiction {jurisdiction_code} not found")
        result = {
            "jurisdiction": j.code,
            "jurisdiction_name": j.name,
            "jurisdiction_short": j.short_name,
            "jurisdiction_type": j.type,
            "country": j.country,
            "brand_color": j.brand_color,
        }
        if j.brand_color_light:
            result["brand_color_light"] = j.brand_color_light
        if j.accent_color:
            result["accent_color"] = j.accent_color
        if j.parent:
            result["parent_jurisdiction"] = j.parent
        if j.last_updated:
            result["last_updated"] = j.last_updated
        if j.legislation_source:
            result["legislation_source"] = j.legislation_source
        if j.mandate_source_type:
            result["mandate_source_type"] = j.mandate_source_type
        result["org_unit_label"] = j.org_unit_label
        result["goal_label"] = j.goal_label
        result["main_service_label"] = j.main_service_label
        result["channel_types"] = j.channel_types
        if j.reach_tiers:
            result["reach_tiers"] = j.reach_tiers
        if j.impact_categories:
            result["impact_categories"] = j.impact_categories
        return result

    def export_entities_index(self, jurisdiction_code: str) -> list[dict]:
        entities = self.list_entities(jurisdiction_code)
        result = []
        for e in entities:
            d = {"prefix": e.prefix, "name": e.name, "short_name": e.short_name}
            if e.blurb:
                d["blurb"] = e.blurb
            if e.is_test:
                d["is_test"] = True
            result.append(d)
        return result

    def export_jurisdictions_index(self) -> list[dict]:
        jurisdictions = self.list_jurisdictions()
        result = []
        for j in jurisdictions:
            d = {"code": j.code, "name": j.name, "short_name": j.short_name,
                 "country": j.country, "type": j.type}
            if j.parent:
                d["parent"] = j.parent
            if j.path:
                d["path"] = j.path
            result.append(d)
        return result

    # ── Validation ────────────────────────────────────────────

    def validate(self) -> list[str]:
        warnings = []

        # Check services without taxonomy
        rows = self.conn.execute(
            "SELECT name, main_service_id FROM supporting_services WHERE taxonomy_json IS NULL").fetchall()
        for r in rows:
            warnings.append(f"Supporting service missing taxonomy: {r['name']}")

        # Check broken relationships
        all_names = set()
        for r in self.conn.execute("SELECT name FROM supporting_services").fetchall():
            all_names.add(r["name"])
        for r in self.conn.execute("SELECT name FROM foundational_services WHERE is_string=0").fetchall():
            all_names.add(r["name"])

        for r in self.conn.execute("SELECT taxonomy_json FROM supporting_services WHERE taxonomy_json IS NOT NULL").fetchall():
            tax = json.loads(r["taxonomy_json"])
            for rel in tax.get("relationships", []):
                if rel.get("service") and rel["service"] not in all_names:
                    warnings.append(f"Broken relationship: '{rel['service']}' not found")

        return warnings

    # ── Stats ─────────────────────────────────────────────────

    def stats(self) -> dict:
        def count(table):
            return self.conn.execute(f"SELECT COUNT(*) as c FROM {table}").fetchone()["c"]
        return {
            "jurisdictions": count("jurisdictions"),
            "entities": count("entities"),
            "goals": count("goals"),
            "main_services": count("main_services"),
            "supporting_services": count("supporting_services"),
            "foundational_services": count("foundational_services"),
            "acts": count("acts"),
            "act_sections": count("act_sections"),
            "section_services": count("section_services"),
        }

    # ── Private Helpers ───────────────────────────────────────

    def _compute_filters(self, entity_prefix, jurisdiction_code):
        """Compute channel_filters, user_group_filters, channel_types, digital_channels."""
        j = self.get_jurisdiction(jurisdiction_code)
        ct = j.channel_types if j else {}

        # Collect all channels and user groups from this entity's services
        channel_codes = set()
        user_groups = set()

        # Get all goals for this entity
        goals = self.conn.execute(
            "SELECT id FROM goals WHERE entity_prefix=? AND jurisdiction_code=?",
            (entity_prefix, jurisdiction_code)).fetchall()

        for g in goals:
            for ms in self.conn.execute("SELECT id FROM main_services WHERE goal_id=?", (g["id"],)).fetchall():
                for ss in self.conn.execute("SELECT channels_json, user_groups_json FROM supporting_services WHERE main_service_id=?", (ms["id"],)).fetchall():
                    for ch in json.loads(ss["channels_json"] or "[]"):
                        if isinstance(ch, dict):
                            channel_codes.add(ch.get("type", ""))
                    for ug in json.loads(ss["user_groups_json"] or "[]"):
                        user_groups.add(ug)

        # Build channel_filters from jurisdiction channel_types
        channel_filters = []
        for code in ct:
            if code in channel_codes:
                info = ct[code]
                channel_filters.append({
                    "code": code,
                    "label": info.get("label", code),
                    "bg_color": info.get("bg", info.get("bg_color", "")),
                    "text_color": info.get("fg", info.get("text_color", "")),
                })

        # Build channel_types dict for export
        export_ct = {}
        for code, info in ct.items():
            export_ct[code] = {
                "label": info.get("label", code),
                "bg_color": info.get("bg", info.get("bg_color", "")),
                "text_color": info.get("fg", info.get("text_color", "")),
            }
            if info.get("border"):
                export_ct[code]["border_color"] = info["border"]

        digital_channels = [code for code, info in ct.items() if info.get("digital", False)]

        return {
            "channel_filters": channel_filters,
            "user_group_filters": sorted(user_groups),
            "channel_types": export_ct,
            "digital_channels": digital_channels,
        }


# ── Row → Model converters ───────────────────────────────────

def _row_to_jurisdiction(row) -> Jurisdiction:
    return Jurisdiction(
        code=row["code"], name=row["name"], short_name=row["short_name"],
        country=row["country"], type=row["type"], parent=row["parent"],
        path=row["path"],
        brand_color=row["brand_color"], brand_color_light=row["brand_color_light"],
        accent_color=row["accent_color"], org_unit_label=row["org_unit_label"],
        goal_label=row["goal_label"], main_service_label=row["main_service_label"],
        last_updated=row["last_updated"], legislation_source=row["legislation_source"],
        mandate_source_type=row["mandate_source_type"],
        channel_types=json.loads(row["channel_types_json"] or "{}"),
        reach_tiers=json.loads(row["reach_tiers_json"]) if row["reach_tiers_json"] else None,
        impact_categories=json.loads(row["impact_categories_json"]) if row["impact_categories_json"] else None,
    )

def _row_to_entity(row) -> Entity:
    return Entity(
        prefix=row["prefix"], jurisdiction_code=row["jurisdiction_code"],
        name=row["name"], short_name=row["short_name"],
        blurb=row["blurb"], nav_name=row["nav_name"],
        has_registry_agents=bool(row["has_registry_agents"]),
        is_test=bool(row["is_test"]),
        mandate_date=row["mandate_date"], mandate_minister=row["mandate_minister"],
        mandate_pdf=row["mandate_pdf"],
        cross_cutting=json.loads(row["cross_cutting_json"] or "[]"),
        mandate_legend=json.loads(row["mandate_legend_json"] or "[]"),
    )

def _row_to_goal(row) -> Goal:
    return Goal(
        id=row["id"], entity_prefix=row["entity_prefix"],
        jurisdiction_code=row["jurisdiction_code"],
        number=row["number"], color=row["color"], title=row["title"],
        short_name=row["short_name"], legend_label=row["legend_label"],
        description=row["description"],
    )

def _row_to_act(row) -> Act:
    return Act(
        id=row["id"], entity_prefix=row["entity_prefix"],
        jurisdiction_code=row["jurisdiction_code"],
        abbrev=row["abbrev"], full_name=row["full_name"], color=row["color"],
        citation=row["citation"], summary=row["summary"], full_text=row["full_text"],
        sort_order=row["sort_order"],
    )

def _row_to_supporting(row) -> SupportingService:
    tax_json = row["taxonomy_json"]
    taxonomy = _parse_taxonomy(json.loads(tax_json)) if tax_json else None
    channels = [Channel(**c) for c in json.loads(row["channels_json"] or "[]")]
    legislation = [LegislationRef(**l) for l in json.loads(row["legislation_json"] or "[]")]
    return SupportingService(
        id=row["id"], main_service_id=row["main_service_id"],
        name=row["name"], desc=row["desc_text"], users=row["users"],
        user_groups=json.loads(row["user_groups_json"] or "[]"),
        channels=channels, legislation=legislation,
        mandate_tags=json.loads(row["mandate_tags_json"] or "[]"),
        taxonomy=taxonomy,
    )

def _row_to_foundational(row) -> FoundationalService:
    if row["is_string"]:
        return FoundationalService(
            id=row["id"], parent_type=row["parent_type"],
            is_string=True, string_value=row["string_value"])

    tax_json = row["taxonomy_json"]
    taxonomy = _parse_taxonomy(json.loads(tax_json)) if tax_json else None
    channels = [Channel(**c) for c in json.loads(row["channels_json"] or "[]")]
    legislation = [LegislationRef(**l) for l in json.loads(row["legislation_json"] or "[]")]
    return FoundationalService(
        id=row["id"], parent_type=row["parent_type"],
        source_id=row["source_id"], name=row["name"],
        desc=row["desc_text"], users=row["users"],
        user_groups=json.loads(row["user_groups_json"] or "[]"),
        channels=channels, legislation=legislation,
        mandate_tags=json.loads(row["mandate_tags_json"] or "[]"),
        taxonomy=taxonomy,
    )

def _parse_taxonomy(data: dict) -> Taxonomy:
    rels = [Relationship(**r) for r in data.get("relationships", [])]
    t = Taxonomy(track=data.get("track", ""), relationships=rels)
    if t.track == "both":
        ind = data.get("individual", {})
        bus = data.get("business", {})
        t.individual_tier = ind.get("tier")
        t.individual_domain = ind.get("domain")
        t.business_tier = bus.get("tier")
        t.business_domain = bus.get("domain")
    else:
        t.tier = data.get("tier")
        t.domain = data.get("domain")
    return t


# ── Export helpers ────────────────────────────────────────────

def _export_supporting(row) -> dict:
    d = {"name": row["name"]}
    if row["desc_text"]:
        d["desc"] = row["desc_text"]
    if row["users"]:
        d["users"] = row["users"]
    d["user_groups"] = json.loads(row["user_groups_json"] or "[]")
    d["channels"] = json.loads(row["channels_json"] or "[]")
    d["legislation"] = json.loads(row["legislation_json"] or "[]")
    d["mandate_tags"] = json.loads(row["mandate_tags_json"] or "[]")
    if row["taxonomy_json"]:
        d["taxonomy"] = json.loads(row["taxonomy_json"])
    # Merge any extra fields back into the output
    extra = json.loads(row["extra_json"] or "{}")
    d.update(extra)
    return d

def _export_foundational(row) -> any:
    if row["is_string"]:
        return row["string_value"]
    d = {}
    if row["source_id"]:
        d["id"] = row["source_id"]
    d["name"] = row["name"]
    if row["desc_text"]:
        d["desc"] = row["desc_text"]
    if row["users"]:
        d["users"] = row["users"]
    ug = json.loads(row["user_groups_json"] or "[]")
    if ug:
        d["user_groups"] = ug
    ch = json.loads(row["channels_json"] or "[]")
    d["channels"] = ch  # always include for foundational
    leg = json.loads(row["legislation_json"] or "[]")
    d["legislation"] = leg  # always include
    mt = json.loads(row["mandate_tags_json"] or "[]")
    if mt:
        d["mandate_tags"] = mt
    if row["taxonomy_json"]:
        d["taxonomy"] = json.loads(row["taxonomy_json"])
    return d


# ── Serialization helpers ─────────────────────────────────────

def _channel_to_dict(c: Channel) -> dict:
    d = {"type": c.type, "label": c.label}
    if c.url:
        d["url"] = c.url
    return d

def _legref_to_dict(l: LegislationRef) -> dict:
    return {"abbrev": l.abbrev, "color": l.color, "full_name": l.full_name}

def _taxonomy_to_json(t: Optional[Taxonomy]) -> Optional[str]:
    if not t:
        return None
    d = {"track": t.track}
    if t.track == "both":
        d["individual"] = {"tier": t.individual_tier, "domain": t.individual_domain}
        d["business"] = {"tier": t.business_tier, "domain": t.business_domain}
    else:
        d["tier"] = t.tier
        d["domain"] = t.domain
    if t.relationships:
        d["relationships"] = [{"type": r.type, "service": r.service, "ministry": r.ministry}
                              for r in t.relationships]
    return json.dumps(d)

def _opt_json(val) -> Optional[str]:
    return json.dumps(val) if val else None
