# Service-types analysis

Working files for the service-types analysis pulled from the 28 Alberta ministry maps in this repo. The output lives at `data/ab/service_types.json` (data) and `data/ab/service_types.md` (human summary).

## What's here

The analysis ran in 4 phases. Each script and its output sit together in this folder.

| Phase | Script | Output | What happens |
|---|---|---|---|
| 1 | `classify_by_task.py` | `phase-1-classification.json` | Walks every supporting service in `data/ab/`. Classifies each by primary service task (Apply / Transact / Check / Report / Engage / Find / Advise) using channel signals plus name-pattern overrides. |
| 2 | `cluster_within_task.py` | `phase-2-clusters-raw.md` | Within each task bucket, groups services by leading-verb name patterns. Reports leverage stats (services × ministries) per candidate cluster. |
| 2 (curated) | _(by hand)_ | `phase-2-clusters.md` | Curated list of service-type candidates with leverage estimates, intent tagging, and shared-shape notes. **Snapshot** from mid-analysis — not synced with the final artifact (a couple of types changed in Phase 4). |
| 3 (curated) | _(by hand)_ | `phase-3-mappings.md` | Per-type cross-reference to the GoA design system docs site: existing examples, productType assignments, gaps, proposed new examples. |
| 4 | `build_service_types.py` | `data/ab/service_types.json` | Mechanically derives the final artifact: assigns each service in the corpus to one of 14 types using matchers, computes leverage stats, attaches the hand-authored content from Phase 2 and Phase 3. |
| 4 audit | _(side output)_ | `phase-4-uncategorised.txt` | Services that didn't fit any of the 14 types — the brief's allowed 20% edge cases. |

`sample_buckets.py` is a small sampler used during Phase 1 to sanity-check what fell into each task bucket.

## Re-running

```
cd analysis/service-types
python3 classify_by_task.py     # regenerate phase-1
python3 cluster_within_task.py  # regenerate phase-2 raw clusters
python3 build_service_types.py  # rebuild data/ab/service_types.json
```

`build_service_types.py` reads `phase-1-classification.json` and the matchers + curated content baked into the script; it writes the final artifact at `data/ab/service_types.json`.

## Constraints applied

The matchers in `build_service_types.py` were designed under three constraints:

1. **Citizen-side only.** Worker-side service types (intake-and-assess, case management, decision adjudication) get a follow-up analysis, not this one.
2. **No product demo data.** Earlier pattern analysis from product demos (140 patterns across 13 ministries) was deliberately deferred. Demos can carry user-bias and broken designs that bias the system view. This analysis draws from the ministry maps directly.
3. **80% coverage, leverage-bar enforced.** Each service type needs 5+ services across 3+ ministries. Sub-types that don't pass are flagged, not stretched. 38 edge cases (~6%) sit outside the 14 types — that's intentional.

## Notes for re-runs

- Adding services to ministry maps or changing channel tags will shift the classification. Expect numbers to drift on re-run; the type list and shapes are stable.
- The matchers are keyword-and-pattern-based. Spot-check the output (`python3 sample_buckets.py` reads phase-1 and dumps random samples per task) before treating it as final. Real false positives caught and fixed in this pass: program names containing "renewal" matched the renew matcher; "Open a government-matched farm savings account" matched the licence matcher when it should have been a benefit.
- If you change matchers, make sure the leverage bar still passes for every type before shipping. The build script prints a `✓` / `✗` per type.

## Next passes

This is the first pass. The methodology is designed to be re-run, but the *content* — the gaps and proposed examples per type — wants further critical review before downstream wiring depends on it.

Planned passes:

- **Critical sweep + prioritization.** Re-read each type's gaps and proposed examples with fresh eyes; de-duplicate where they overlap across types (status trackers, decision letters, eligibility checks recur); apply priority signals (service-type weight × gap reach) so downstream wiring surfaces high-leverage content first. Runs before the wiring brief that consumes this output.

- **Worker-side service types.** This pass covered citizen-side only. Worker-side types (intake-and-assess, case management, the back-half of every citizen service) are the natural follow-up, derived from each citizen-side type they pair with. The ALSS pilot is the first instance walking the full pipeline.

- **Cross-jurisdictional comparison.** Once another province or the federal data come online, comparing service types across jurisdictions earns the Kate Tarling vocabulary its keep — "all Getting permission services across AB / BC / federal" becomes a real query.
