# Ministry Reorganization History — Deferred Design Note

**Status:** DEFERRED. Do not implement yet.
**Revisit when:** (a) all Alberta ministries are complete, or (b) we begin cross-jurisdictional analysis.
**Captured:** 2026-04-09 (during Phase 1 research on Forestry and Parks)

---

## The observation

Ministry boundaries move around a lot, and the current schema has no place to record that. While researching Forestry and Parks, the reorganization history was impossible to ignore:

- Pre-2022: forest management sat under "Agriculture, Forestry and Rural Economic Development"; parks sat under "Environment and Parks"
- Oct 2022: Premier Smith split Environment and Parks into (a) Environment and Protected Areas and (b) Forestry, Parks and Tourism
- 2023: Tourism file moved elsewhere; ministry renamed to "Forestry and Parks"

Each of those moves changed *who delivers what* without changing *what gets delivered*. From a citizen's perspective, the services stayed roughly the same — the org chart churned underneath.

This is analogous to the service-types insight: the structure of a service is stable, the delivery changes. Ministry structure is the *organizational* layer of delivery churn, and it's the layer most prone to political reshuffling.

## Why it could matter later

Three places where this becomes useful, not just interesting:

1. **Cross-jurisdictional comparison.** "Which ministry owns forest management?" has a different answer in every province and federally, and the answer changes on a 2-4 year cycle. If we want to compare "all forest management services" across AB, BC, and the feds, we need a way to say "this service was here in 2018, moved here in 2022, and lives here today" so cross-sections line up.

2. **Historical stability metrics.** Once we have a few years of data, we could show which services have been most structurally stable vs. most churned around. Stable services are probably the ones with clearest policy intent; churned services may be the ones with contested ownership.

3. **Minister accountability context.** When a new minister inherits a ministry, the blast radius of what's actually in their portfolio depends on the most recent reorg. A service map that knows about ministry history can answer "what did this minister inherit vs. what did their predecessor own?"

## Possible shapes

Options we could take when we revisit:

- **Ministry-level `history[]` field** on the ministry record: an ordered list of prior ministry names and the dates each was renamed or merged. Simple, low-cost, gives us a breadcrumb trail.

- **Service-level provenance tags:** each supporting service records which ministry it was delivered from at each point in time. Higher fidelity, higher authoring cost, only pays off when we have cross-jurisdictional or historical comparison needs.

- **Separate `reorg-log.json` per jurisdiction:** an event log outside the ministry files, capturing moves as events (split, merge, rename, transfer-service) with dates and sources. Keeps the per-ministry files clean and gives us a single audit trail.

My lean when we pick this up would be **reorg-log.json + simple ministry-level `previous_names[]`**, but worth revisiting once we actually have a use case that demands it (probably cross-jurisdictional).

## When we revisit

Same two triggers as the service-types note:

- After all Alberta ministries are captured. We'll have a large enough sample to see which ministries have histories worth recording.
- When we start a second jurisdiction. That's when "who owns forest management?" becomes a comparison problem instead of a fact.
