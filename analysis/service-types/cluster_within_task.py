#!/usr/bin/env python3
"""
Phase 2: Surface candidate sub-types within each task by clustering on name patterns.

For each task bucket, runs a set of regex patterns against service names. Services
that match a pattern form a candidate cluster. Each cluster reports:
  - service_count, ministry_count (the leverage bar inputs)
  - the services themselves, with ministry, legislation, domain

Output:
  phase-2-clusters-raw.md — per-task candidate clusters with leverage stats and members.

Then I manually curate the final list in phase-2-clusters.md, applying leverage bar
(5+ services across 3+ ministries) and Kate Tarling intent tagging.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent
CLASSIFICATION = ROOT / "phase-1-classification.json"
OUT = ROOT / "phase-2-clusters-raw.md"

# Per-task name-pattern heuristics. Each entry: (cluster_id, regex matched against name).
# Patterns are anchored at name start unless noted. Order matters — first match wins so
# more specific patterns should appear before more general ones.
PATTERNS = {
    "Apply": [
        ("apply-for-a-benefit", r"^(apply for|get) (financial )?(help|support|aid|monthly|income|benefits?)\b"),
        ("apply-for-a-licence", r"^apply for (a |an )?[\w\- ]*?\b(licen[cs]e|certifi(cate|cation))\b"),
        ("apply-for-a-permit", r"^apply for (a |an )?[\w\- ]*?\bpermit\b"),
        ("apply-for-a-grant-or-funding", r"^apply for (a |an )?[\w\- ]*?\b(grant|funding|loan|scholarship|award|subsidy|tax credit|exemption)\b"),
        ("register-a-business-or-thing", r"^register (a|an|as|with|your)\b"),
        ("register-an-event-or-record", r"^register\b"),
        ("apply-other", r"^apply\b"),
        ("get-help-or-support", r"^get (help|support|connected|matched|assistance|emergency)\b"),
        ("get-a-benefit", r"^get [\w\- ]*?(benefits?|support|payments?|monthly|coverage|funding|aid|loan|grant|exemption)"),
        ("get-a-licence-or-permit", r"^get (a |an )?[\w\- ]*?(licen[cs]e|permit|certifi(cate|cation)|registration)\b"),
        ("get-a-card-or-credential", r"^get (a |an )?[\w\- ]*?(card|id|number|credential|recognition)\b"),
        ("nominate-or-recognize", r"^nominate\b"),
        ("enrol-or-attend", r"^(enrol|attend|join)\b"),
        ("submit-information", r"^submit\b"),
        ("buy-or-bid-or-acquire", r"^(buy|bid|acquire|purchase|find and bid)\b"),
        ("manage-or-update-account", r"^(manage|update|change|modify|cancel)\b"),
        ("transfer-or-move", r"^(transfer|move|relocate|import|export)\b"),
        ("become-something", r"^become\b"),
        ("file-or-defer-tax", r"^(file|defer)\b"),
    ],
    "Transact": [
        ("pay-a-fee-or-fine", r"^pay\b"),
        ("renew-a-licence-or-thing", r"^renew\b"),
        ("file-and-pay", r"^file (and pay|.*?and pay)\b"),
        ("file-something", r"^file\b"),
        ("search-records", r"^search [\w\- ]*?\b(records|titles|rights|data|database)\b"),
        ("buy-or-acquire-rights", r"^(buy|acquire|purchase|bid|request a (direct )?(purchase|sale))\b"),
        ("access-account-or-wallet", r"^(access|use|sign in to)\b"),
        ("transact-other", r".*"),
    ],
    "Check": [
        ("check-status", r"^check [\w\- ]*?(status|results|coverage|history|claim|rating)\b"),
        ("manage-account-or-loan", r"^(manage|track and manage)\b"),
        ("get-help-resolving", r"^get help (resolving|preventing)"),
        ("check-other", r"^check\b"),
        ("respond-to", r"^respond to\b"),
        ("access-records-or-data", r"^access [\w\- ]*?(records?|data)\b"),
    ],
    "Report": [
        ("report-a-concern-or-incident", r"^report (a |an )?(concern|incident|safety|suspected|patient|workplace|conflict|bias|abuse|fraud|loss|outbreak)"),
        ("report-emissions-or-regulatory-data", r"^report [\w\- ]*?(emissions|royalties|production|tax|return|safety data|incident database)"),
        ("file-a-complaint", r"^file (a|an) (complaint|grievance|human rights)"),
        ("file-a-tip-or-disclosure", r"^(file|submit) (a|an)? ?(tip|disclosure)"),
        ("submit-a-complaint", r"^submit (a|an) (complaint|grievance|concern)"),
        ("submit-a-report", r"^submit (a|an) (report|tip)"),
        ("make-a-complaint-or-disclosure", r"^make (a|an) (complaint|disclosure|report)"),
        ("report-other", r"^report\b"),
    ],
    "Find": [
        ("find-a-service-or-place", r"^find (a |an )?[\w\- ]*?(service|location|centre|provider|professional|advisor|office|clinic|shelter|organization|coach|mentor|fund)"),
        ("find-information-or-resource", r"^find\b"),
        ("search-database-or-records", r"^search\b"),
        ("look-up-something", r"^look up\b"),
        ("learn-about", r"^learn (about|how)\b"),
        ("read-or-access-information", r"^(read|access|view|see) [\w\- ]*?(information|publication|guide|standards|policy|policies|data|records?)"),
        ("check-availability-or-status", r"^check\b"),
        ("get-a-free-thing", r"^get a free\b"),
        ("get-information-or-help", r"^get [\w\- ]*?(information|help|connected|advice|guidance)\b"),
        ("take-a-course-or-training", r"^take (a |an )?[\w\- ]*?(course|training)"),
        ("plan-or-prepare", r"^(plan|prepare|map)\b"),
        ("attend-event", r"^attend\b"),
        ("get-supports-non-digital", r"^get\b"),
    ],
    "Advise": [
        ("access-a-program-or-service", r"^access [\w\- ]*?(program|service|shelter|housing)"),
        ("get-help-with", r"^get help (with|navigating|finding|understanding)"),
        ("get-emergency-or-crisis-support", r"^get [\w\- ]*?(emergency|crisis|outreach|shelter|housing)"),
        ("get-personal-financial-or-legal-support", r"^get [\w\- ]*?(legal|financial|personal|advice|counselling)"),
        ("arrange-something", r"^arrange\b"),
        ("set-up-or-coordinate", r"^(set up|coordinate|align)\b"),
        ("get-inspected-or-certified", r"^get [\w\- ]*?(inspected|certified|approved|reviewed|assessed|evaluated)"),
        ("advise-other-get", r"^get\b"),
        ("advise-other", r".*"),
    ],
    "Engage": [
        ("engage-all", r".*"),
    ],
    "Unclassified": [
        ("unclassified-all", r".*"),
    ],
    "No-channels": [
        ("no-channels-all", r".*"),
    ],
}


def assign_cluster(task, name):
    name = name.strip()
    for cluster_id, pattern in PATTERNS.get(task, []):
        if re.search(pattern, name, re.IGNORECASE):
            return cluster_id
    return "unmatched"


def main():
    data = json.loads(CLASSIFICATION.read_text())
    services = data["services"]

    by_task = defaultdict(list)
    for s in services:
        by_task[s["primary_task"]].append(s)

    lines = ["# Phase 2 — Raw cluster candidates by task\n"]
    lines.append("Generated by `cluster_within_task.py`. Each cluster is a name-pattern bucket.\n")
    lines.append("Leverage bar: cluster passes if `services >= 5` AND `ministries >= 3`.\n")
    lines.append("Curate by hand into `phase-2-clusters.md` after reviewing.\n\n")

    task_order = ["Apply", "Transact", "Check", "Report", "Engage", "Find", "Advise", "Unclassified", "No-channels"]
    for task in task_order:
        bucket = by_task.get(task, [])
        if not bucket:
            continue

        clusters = defaultdict(list)
        for s in bucket:
            cid = assign_cluster(task, s["name"])
            clusters[cid].append(s)

        lines.append(f"\n## {task} ({len(bucket)} services)\n")

        # Sort clusters: leverage-bar passers first, then by service count
        cluster_summary = []
        for cid, members in clusters.items():
            ministries = {m["ministry_prefix"] for m in members}
            passes = len(members) >= 5 and len(ministries) >= 3
            cluster_summary.append((passes, -len(members), cid, members, ministries))
        cluster_summary.sort(key=lambda x: (not x[0], x[1]))

        for passes, _neg_count, cid, members, ministries in cluster_summary:
            mark = "✅" if passes else "❌"
            lines.append(f"\n### {mark} `{cid}` — {len(members)} services, {len(ministries)} ministries\n")
            if not passes:
                if len(members) < 5:
                    lines.append(f"_Below leverage bar (need 5+ services)._\n")
                elif len(ministries) < 3:
                    lines.append(f"_Below leverage bar (only {len(ministries)} ministries; need 3+)._\n")
            for m in sorted(members, key=lambda x: (x["ministry_prefix"], x["name"])):
                doms = m.get("domain") or "—"
                legs = ",".join(m.get("legislation", []) or []) or "—"
                lines.append(f"- **[{m['ministry_prefix']}]** {m['name']} _({doms}, leg: {legs})_")
            lines.append("")

    OUT.write_text("\n".join(lines))
    print(f"Wrote {OUT}")
    print()
    # Summary: passing clusters per task
    print("Passing clusters per task (leverage bar 5+ services, 3+ ministries):")
    for task in task_order:
        bucket = by_task.get(task, [])
        if not bucket:
            continue
        clusters = defaultdict(list)
        for s in bucket:
            clusters[assign_cluster(task, s["name"])].append(s)
        passing = [
            cid for cid, members in clusters.items()
            if len(members) >= 5 and len({m["ministry_prefix"] for m in members}) >= 3
        ]
        print(f"  {task:14s} {len(passing):3d} passing  / {len(clusters):3d} candidate")


if __name__ == "__main__":
    main()
