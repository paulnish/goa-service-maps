#!/usr/bin/env python3
"""
Service map data validator.

Runs the Phase 4 checks described in SKILL.md against a jurisdiction's data:
  1. Schema compliance      — required fields on supporting services
  2. Channel validity       — channel types exist in config.json
  3. Legislation consistency — bidirectional check between ministry and legislation JSON
  4. No orphans             — every supporting belongs to a main, every main to a goal
  5. Filter arrays          — channel_filters / user_group_filters match actual data
  6. Reach coverage         — at least 80% of supporting services have a reach estimate
  7. Naming                 — supporting service names start with a verb

Usage:
    python validate.py <data_dir> [--jurisdiction ab] [--ministry cfs]

    data_dir        Path to the data/ folder (e.g. goa-service-maps/data)
    --jurisdiction  Jurisdiction code to validate. Defaults to all jurisdictions.
    --ministry      Ministry prefix to validate. Defaults to all ministries in the jurisdiction.

Exit code is 0 if all checks pass, 1 if any check fails.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# A small set of English verbs we accept as valid first words for supporting service names.
# This is intentionally permissive — the goal is to catch the "Access Housing Stability Program"
# style of noun-first bureaucratic names, not to enforce a rigid vocabulary.
COMMON_VERBS = {
    "apply", "register", "report", "find", "get", "check", "request", "submit",
    "renew", "update", "file", "pay", "search", "view", "download", "access",
    "book", "schedule", "enroll", "enrol", "join", "start", "create", "cancel",
    "change", "replace", "transfer", "withdraw", "dispute", "appeal", "claim",
    "receive", "obtain", "buy", "order", "reserve", "look", "track", "calculate",
    "complete", "send", "give", "use", "learn", "explore", "manage", "verify",
    "confirm", "return", "exchange", "challenge", "contest", "respond", "seek",
    "sign", "log", "browse", "compare", "estimate", "plan", "build", "design",
    "review", "read", "contact", "call", "visit", "meet", "attend", "participate",
    "volunteer", "donate", "nominate", "vote", "enter", "exit", "leave", "move",
    "travel", "drive", "ride", "fly", "ship", "mail", "deliver", "pick",
    "hire", "retire", "quit", "resign", "fire", "recruit", "interview",
    "save", "invest", "borrow", "lend", "owe", "repay", "refund", "reimburse",
    "inspect", "certify", "license", "permit", "authorize", "approve", "reject",
    "abandon", "adopt", "foster", "sponsor", "support", "help", "assist",
    "prevent", "stop", "resolve", "mediate", "negotiate", "settle",
    "prove", "demonstrate", "show", "tell", "inform", "notify", "alert",
    "include", "exclude", "add", "remove", "delete", "edit", "modify",
    "test", "measure", "score", "rate", "rank", "grade", "evaluate", "assess",
    "oversee", "monitor", "supervise", "audit", "investigate", "research",
    "publish", "share", "post", "announce", "declare", "disclose",
    "protect", "defend", "guard", "secure", "safeguard", "preserve",
    "fund", "finance", "grant", "award", "issue", "distribute", "allocate",
    "restore", "repair", "fix", "maintain", "upgrade", "replace",
    # More verbs commonly used in citizen-facing service names
    "take", "make", "become", "prepare", "earn", "write", "enforce", "arrange",
    "set", "authenticate", "defer", "try", "direct", "complain", "pursue",
    "administer", "prosecute", "adjudicate", "oversee", "challenge", "provide",
    "choose", "select", "pick", "decide", "opt", "prefer", "switch",
    "practise", "practice", "experience", "recreate", "allocate", "cut", "reserve", "hunt", "fish", "camp",
    "collect", "gather", "fetch", "carry", "lift", "move", "push", "pull",
    "operate", "run", "drive", "pilot", "steer", "navigate",
    "keep", "hold", "store", "preserve", "retain", "save",
    "do", "perform", "conduct", "execute", "carry", "handle", "process",
    "rent", "lease", "occupy", "vacate", "evict", "relocate",
    "raise", "lower", "increase", "decrease", "adjust", "tune",
    "grow", "develop", "expand", "shrink", "reduce", "limit",
    "enroll", "register", "sign", "subscribe", "unsubscribe", "opt",
    "teach", "train", "coach", "mentor", "tutor", "educate",
    "study", "practice", "rehearse", "drill", "memorize",
    "buy", "sell", "trade", "barter", "exchange", "swap",
    "cook", "bake", "prepare", "eat", "drink", "taste", "serve",
    "clean", "wash", "scrub", "polish", "sanitize", "disinfect",
    "fight", "defend", "attack", "strike", "punch", "kick",
    "run", "walk", "jog", "sprint", "race", "compete", "play",
    "sleep", "rest", "wake", "nap", "dream",
    "think", "believe", "know", "understand", "comprehend", "realize",
}


class Issue:
    __slots__ = ("check", "severity", "location", "message")

    def __init__(self, check: str, severity: str, location: str, message: str):
        self.check = check
        self.severity = severity  # "error" or "warning"
        self.location = location
        self.message = message

    def __str__(self) -> str:
        marker = "✗" if self.severity == "error" else "⚠"
        return f"  {marker} [{self.check}] {self.location}: {self.message}"


class Validator:
    def __init__(self, data_dir: Path, jurisdiction: str, ministry: dict, config: dict,
                 legislation: dict | None = None):
        self.data_dir = data_dir
        self.jurisdiction = jurisdiction
        self.ministry = ministry
        self.config = config
        self.legislation = legislation
        self.prefix = ministry.get("prefix", "?")
        self.issues: list[Issue] = []

    def err(self, check: str, location: str, message: str) -> None:
        self.issues.append(Issue(check, "error", location, message))

    def warn(self, check: str, location: str, message: str) -> None:
        self.issues.append(Issue(check, "warning", location, message))

    # ------------------------------------------------------------------ iterators

    def iter_supporting(self):
        """Yield (goal, main_service, service, location_str, is_foundational) for each service
        that carries citizen-facing data (name, channels, legislation, etc.).

        Foundational services are included when they are defined as full objects (dicts),
        because they follow the same schema as regular supporting services and can carry
        legislation and mandate tags. String-form foundational services are skipped —
        they're just labels referring to services defined elsewhere.
        """
        # Ministry-level foundational services
        for fs in self.ministry.get("foundational_services", []) or []:
            if isinstance(fs, dict):
                loc = f"ministry foundational / '{fs.get('name', '?')}'"
                yield None, None, fs, loc, True

        for goal in self.ministry.get("goals", []):
            gnum = goal.get("number", "?")
            # Goal-level foundational services
            for fs in goal.get("foundational_services", []) or []:
                if isinstance(fs, dict):
                    loc = f"goal {gnum} foundational / '{fs.get('name', '?')}'"
                    yield goal, None, fs, loc, True

            for ms in goal.get("main_services", []):
                msnum = ms.get("number", "?")
                # Main-service-level foundational services
                for fs in ms.get("foundational_services", []) or []:
                    if isinstance(fs, dict):
                        loc = f"goal {gnum} / ms {msnum} foundational / '{fs.get('name', '?')}'"
                        yield goal, ms, fs, loc, True
                for s in ms.get("supporting", []):
                    loc = f"goal {gnum} / ms {msnum} / '{s.get('name', '?')}'"
                    yield goal, ms, s, loc, False

    # ------------------------------------------------------------------ checks

    def check_schema(self) -> None:
        """1. Schema compliance — required fields on supporting services."""
        required = ["name", "desc", "users", "user_groups", "channels"]
        for _, _, s, loc, is_foundational in self.iter_supporting():
            for field in required:
                if field not in s:
                    self.err("schema", loc, f"missing required field '{field}'")
                elif field in ("user_groups", "channels") and not isinstance(s[field], list):
                    self.err("schema", loc, f"'{field}' must be a list")
                elif field == "channels" and not s[field] and not is_foundational:
                    # Foundational services legitimately may have empty channels (internal/oversight)
                    self.err("schema", loc, "channels list is empty — every service needs at least one channel")
                elif field in ("name", "desc", "users") and not s[field]:
                    self.err("schema", loc, f"'{field}' is empty")

    def check_channel_validity(self) -> None:
        """2. Every channel type exists in config.json."""
        valid_types = set(self.config.get("channel_types", {}).keys())
        for _, _, s, loc, _ in self.iter_supporting():
            for ch in s.get("channels", []):
                ch_type = ch.get("type")
                if not ch_type:
                    self.err("channel-validity", loc, "channel is missing 'type'")
                elif ch_type not in valid_types:
                    self.err("channel-validity", loc,
                             f"unknown channel type '{ch_type}' (not in config.json)")
                if not ch.get("label"):
                    self.warn("channel-validity", loc, f"channel '{ch_type}' has no label")

    def check_legislation_consistency(self) -> None:
        """3. Bidirectional check between ministry JSON and legislation JSON."""
        if not self.legislation:
            return  # no legislation file for this ministry

        # Build sets of (act_abbrev, service_name) from both files
        ministry_pairs: set[tuple[str, str]] = set()
        for _, _, s, _, _ in self.iter_supporting():
            name = s.get("name", "")
            for leg in s.get("legislation", []):
                abbrev = leg.get("abbrev")
                if abbrev:
                    ministry_pairs.add((abbrev, name))

        legislation_pairs: set[tuple[str, str]] = set()
        act_abbrevs_in_leg: set[str] = set()
        for act in self.legislation.get("acts", []):
            abbrev = act.get("abbrev")
            if abbrev:
                act_abbrevs_in_leg.add(abbrev)
            for section in act.get("sections", []):
                for svc in section.get("services", []):
                    if abbrev and svc.get("name"):
                        legislation_pairs.add((abbrev, svc["name"]))

        # Services that claim legislation on the ministry side but aren't in the legislation file
        orphan_ministry = ministry_pairs - legislation_pairs
        for abbrev, name in sorted(orphan_ministry):
            self.err("legislation-consistency",
                     f"ministry.{self.prefix}",
                     f"'{name}' has legislation '{abbrev}' but no matching entry in "
                     f"{self.prefix}_legislation.json")

        # Entries in the legislation file that reference services not found in the ministry
        orphan_legislation = legislation_pairs - ministry_pairs
        for abbrev, name in sorted(orphan_legislation):
            self.err("legislation-consistency",
                     f"legislation.{self.prefix}",
                     f"act '{abbrev}' references service '{name}' but it is not listed with "
                     f"that legislation in {self.prefix}.json")

        # Acts referenced by services but not defined in the legislation file
        referenced_acts = {abbrev for abbrev, _ in ministry_pairs}
        undefined_acts = referenced_acts - act_abbrevs_in_leg
        for abbrev in sorted(undefined_acts):
            self.err("legislation-consistency",
                     f"legislation.{self.prefix}",
                     f"act '{abbrev}' is referenced by services but has no entry in acts[]")

    def check_no_orphans(self) -> None:
        """4. Every goal/main-service/supporting is properly nested."""
        if not self.ministry.get("goals"):
            self.err("orphans", f"ministry.{self.prefix}", "ministry has no goals")
            return

        for goal in self.ministry.get("goals", []):
            if "number" not in goal:
                self.err("orphans", f"ministry.{self.prefix}", "goal missing 'number'")
            if not goal.get("main_services"):
                self.warn("orphans",
                          f"goal {goal.get('number', '?')}",
                          "goal has no main services")
                continue
            for ms in goal["main_services"]:
                if "number" not in ms:
                    self.err("orphans",
                             f"goal {goal.get('number', '?')}",
                             f"main service '{ms.get('name', '?')}' missing 'number'")
                if not ms.get("supporting"):
                    self.warn("orphans",
                              f"goal {goal.get('number', '?')} / ms {ms.get('number', '?')}",
                              f"main service '{ms.get('name', '?')}' has no supporting services")

    def check_filter_arrays(self) -> None:
        """5. channel_filters and user_group_filters match the actual data."""
        actual_channels: set[str] = set()
        actual_groups: set[str] = set()
        for _, _, s, _, _ in self.iter_supporting():
            for ch in s.get("channels", []):
                if ch.get("type"):
                    actual_channels.add(ch["type"])
            for g in s.get("user_groups", []):
                if g:
                    actual_groups.add(g)

        # channel_filters may be either a list of strings or a list of dicts with {code, label, ...}
        raw_channel_filters = self.ministry.get("channel_filters", [])
        declared_channels: set[str] = set()
        for cf in raw_channel_filters:
            if isinstance(cf, str):
                declared_channels.add(cf)
            elif isinstance(cf, dict) and cf.get("code"):
                declared_channels.add(cf["code"])

        # user_group_filters may similarly be strings or dicts
        raw_group_filters = self.ministry.get("user_group_filters", [])
        declared_groups: set[str] = set()
        for gf in raw_group_filters:
            if isinstance(gf, str):
                declared_groups.add(gf)
            elif isinstance(gf, dict) and gf.get("label"):
                declared_groups.add(gf["label"])

        missing_channels = actual_channels - declared_channels
        extra_channels = declared_channels - actual_channels
        missing_groups = actual_groups - declared_groups
        extra_groups = declared_groups - actual_groups

        for ch in sorted(missing_channels):
            self.err("filter-arrays", f"ministry.{self.prefix}",
                     f"channel_filters missing '{ch}' (used by supporting services)")
        for ch in sorted(extra_channels):
            self.warn("filter-arrays", f"ministry.{self.prefix}",
                      f"channel_filters includes '{ch}' but no service uses it")
        for g in sorted(missing_groups):
            self.err("filter-arrays", f"ministry.{self.prefix}",
                     f"user_group_filters missing '{g}' (used by supporting services)")
        for g in sorted(extra_groups):
            self.warn("filter-arrays", f"ministry.{self.prefix}",
                      f"user_group_filters includes '{g}' but no service uses it")

        # digital_channels should equal the subset of actual_channels marked digital in config
        config_digital = {
            code for code, spec in self.config.get("channel_types", {}).items()
            if spec.get("digital")
        }
        expected_digital = actual_channels & config_digital
        declared_digital = set(self.ministry.get("digital_channels", []))
        if expected_digital != declared_digital:
            missing = expected_digital - declared_digital
            extra = declared_digital - expected_digital
            if missing:
                self.err("filter-arrays", f"ministry.{self.prefix}",
                         f"digital_channels missing: {sorted(missing)}")
            if extra:
                self.warn("filter-arrays", f"ministry.{self.prefix}",
                          f"digital_channels has unused: {sorted(extra)}")

    def check_reach_coverage(self) -> None:
        """6. At least 80% of non-foundational supporting services have a reach estimate.

        Foundational services are excluded because they're internal capabilities and don't
        have a meaningful citizen-facing reach number.
        """
        total = 0
        with_reach = 0
        for _, _, s, loc, is_foundational in self.iter_supporting():
            if is_foundational:
                continue
            total += 1
            reach = s.get("reach")
            if reach and isinstance(reach, dict) and reach.get("tier"):
                with_reach += 1
                valid_tiers = set(self.config.get("reach_tiers", {}).keys())
                if reach["tier"] not in valid_tiers and reach["tier"] != "unknown":
                    self.err("reach-coverage", loc,
                             f"reach tier '{reach['tier']}' is not defined in config.json reach_tiers")

        if total == 0:
            return
        coverage = with_reach / total
        if coverage < 0.80:
            self.warn("reach-coverage", f"ministry.{self.prefix}",
                      f"only {with_reach}/{total} ({coverage:.0%}) of supporting services have reach "
                      f"estimates — target is 80%")

    def check_naming(self) -> None:
        """7. Supporting service names should start with a verb."""
        for _, _, s, loc, _ in self.iter_supporting():
            name = (s.get("name") or "").strip()
            if not name:
                continue  # already flagged by schema check
            first_word = re.split(r"[\s\-/]", name.lower(), maxsplit=1)[0]
            # Strip punctuation
            first_word = re.sub(r"[^\w']", "", first_word)
            if first_word not in COMMON_VERBS:
                self.warn("naming", loc,
                          f"name does not start with a recognized verb ('{first_word}') — "
                          f"consider an action-oriented phrasing")

    # ------------------------------------------------------------------ run

    def run(self) -> list[Issue]:
        self.check_schema()
        self.check_channel_validity()
        self.check_legislation_consistency()
        self.check_no_orphans()
        self.check_filter_arrays()
        self.check_reach_coverage()
        self.check_naming()
        return self.issues


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate_jurisdiction(data_dir: Path, juris: str, ministry_filter: str | None) -> int:
    juris_dir = data_dir / juris
    if not juris_dir.exists():
        print(f"✗ Jurisdiction '{juris}' not found at {juris_dir}")
        return 1

    config_path = juris_dir / "config.json"
    if not config_path.exists():
        print(f"✗ {juris}: config.json not found at {config_path}")
        return 1
    config = load_json(config_path)

    ministries_path = juris_dir / "ministries.json"
    if not ministries_path.exists():
        print(f"✗ {juris}: ministries.json not found")
        return 1
    ministries_index = load_json(ministries_path)

    total_errors = 0
    total_warnings = 0
    validated = 0

    for entry in ministries_index:
        prefix = entry.get("prefix")
        if not prefix:
            continue
        if ministry_filter and prefix != ministry_filter:
            continue
        if entry.get("is_test"):
            continue  # skip test ministries

        ministry_path = juris_dir / f"{prefix}.json"
        if not ministry_path.exists():
            print(f"✗ {juris}/{prefix}: ministry file not found at {ministry_path}")
            total_errors += 1
            continue

        ministry = load_json(ministry_path)

        leg_path = juris_dir / f"{prefix}_legislation.json"
        legislation = load_json(leg_path) if leg_path.exists() else None

        validator = Validator(data_dir, juris, ministry, config, legislation)
        issues = validator.run()

        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        status = "✓" if not errors else "✗"
        print(f"\n{status} {juris}/{prefix} — {len(errors)} error(s), {len(warnings)} warning(s)")
        for issue in issues:
            print(issue)

        total_errors += len(errors)
        total_warnings += len(warnings)
        validated += 1

    if validated == 0:
        if ministry_filter:
            print(f"✗ Ministry '{ministry_filter}' not found in {juris}/ministries.json")
            return 1
        print(f"⚠ {juris}: no ministries found to validate")
        return 0

    print(f"\n{'─' * 60}")
    print(f"Summary: {validated} ministries validated, "
          f"{total_errors} error(s), {total_warnings} warning(s)")
    return 0 if total_errors == 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_dir", type=Path, help="Path to the data/ folder")
    parser.add_argument("--jurisdiction", help="Jurisdiction code (e.g. ab). Default: all jurisdictions.")
    parser.add_argument("--ministry", help="Ministry prefix (e.g. cfs). Default: all ministries.")
    args = parser.parse_args()

    data_dir: Path = args.data_dir
    if not data_dir.exists():
        print(f"✗ Data directory not found: {data_dir}")
        return 1

    if args.jurisdiction:
        jurisdictions = [args.jurisdiction]
    else:
        jurisdictions_path = data_dir / "jurisdictions.json"
        if jurisdictions_path.exists():
            jurisdictions = [j["code"] for j in load_json(jurisdictions_path)]
        else:
            # Fallback: any folder with a config.json
            jurisdictions = sorted(
                p.name for p in data_dir.iterdir()
                if p.is_dir() and (p / "config.json").exists()
            )

    overall_status = 0
    for juris in jurisdictions:
        rc = validate_jurisdiction(data_dir, juris, args.ministry)
        if rc != 0:
            overall_status = rc

    return overall_status


if __name__ == "__main__":
    sys.exit(main())
