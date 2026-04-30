#!/usr/bin/env python3
"""Sample 8-12 services from each task bucket to sanity-check the classifier."""

import json
import random
from pathlib import Path

DATA = Path(__file__).parent / "phase-1-classification.json"
random.seed(42)


def main():
    data = json.loads(DATA.read_text())
    by_task = {}
    for s in data["services"]:
        by_task.setdefault(s["primary_task"], []).append(s)

    order = ["Apply", "Transact", "Check", "Report", "Engage", "Find", "Advise", "Unclassified", "No-channels"]
    # Show any task we didn't anticipate at the end.
    for task in list(by_task.keys()):
        if task not in order:
            order.append(task)

    for task in order:
        bucket = by_task.get(task, [])
        if not bucket:
            continue
        print(f"\n=== {task} ({len(bucket)}) ===")
        sample = random.sample(bucket, min(10, len(bucket)))
        for s in sample:
            channels = ",".join(s["channels"]) if s["channels"] else "(no channels)"
            print(f"  [{s['ministry_prefix']}] {s['name']}")
            print(f"      channels: {channels}")
            sig = s.get("signals", {})
            flags = [k for k, v in sig.items() if v]
            if flags:
                print(f"      signals: {','.join(flags)}")


if __name__ == "__main__":
    main()
