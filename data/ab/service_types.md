# Alberta Service Types

A human-readable summary of the service-types analysis pulled from the 28 ministry maps in this repo. The structured data lives next to this file in `service_types.json`; this doc is the orientation pass.

## What this is

For any given service in Alberta — say, "Apply for income support" — this analysis answers: what kind of service is it (in the design system / shape sense)? Which other services across ministries share its shape? Which patterns and components down the design system stack are reachable from it?

A **service type** is a `(service task × Kate Tarling intent)` cluster validated by a leverage bar (5+ services across 3+ ministries). It's the most stable thing about a service — channels and legislation change, the type rarely does.

## Three axes

Each service type sits at the intersection of three orthogonal axes — same services, three different lenses.

1. **Service task** — *how* the citizen interacts. Apply / Transact / Check / Report / Engage / Find / Advise. Derived from the channels each service uses.

2. **Kate Tarling intent** — *what kind of thing* the service is at policy level. The canonical nine from Kate Tarling (getting financial support, getting permission, paying for something, and so on). A service type can carry more than one intent when the data warrants.

3. **Navigation taxonomy** — *where* the service lives by topic. Built by Paul, already in `data/ab/taxonomy.json` and tagged on every supporting service. Three nested fields plus cross-service links:
   - `track` — *individual* or *business*. Is the citizen acting in their personal capacity or as an organization?
   - `tier` — the major bucket within the track. Individual tiers: core human needs, societal needs and supports, scenario-dependent, identity-and-credentials. Business tiers: core business needs, regulatory and compliance, scenario-dependent, industry-specific.
   - `domain` — the topic. _Health, education, driving, housing, licences and permits, agriculture, etc._
   - `relationships[]` — cross-service links like Worker↔Employer or Consumer↔Regulated provider.

The same service type cuts across many domains. `apply-for-a-benefit` is the same shape whether it's "Apply for income support" (individual / core_human_needs / money_taxes_benefits) or "Apply for a student loan" (individual / core_human_needs / education_training) or "Apply for childcare subsidy" (individual / core_human_needs / family_relationships). The **shape** (service type) is what design teams build for; the **topic** (navigation taxonomy) is what citizens browse by.

## Service tasks (7)

| Task | What the citizen does |
|---|---|
| **Apply** | Demonstrates eligibility, submits, waits for a decision |
| **Transact** | Pays, renews, files, buys — completes a routine exchange |
| **Check** | Looks up status, records, history (authenticated to themselves) |
| **Report** | Pushes information about a hazard or third party |
| **Engage** | Participates in a consultation or decision process |
| **Find** | Looks up information, services, or providers |
| **Advise** | Gets human-mediated help; no digital action surface today |

The original framing had 5 tasks (Apply / Transact / Check / Report / Engage). **Find** and **Advise** were added because the data demanded — together they cover ~50% of GoA services. Half the corpus is discovery-only or in-person-only.

## Kate Tarling's nine intents

Adapted from Kate Tarling's *The Service Organization*. Each service type is tagged with one or more of these:

1. Registering, providing or reporting information
2. Requesting, sharing or checking information
3. Paying for something
4. Getting financial support or claiming something
5. Getting permission to do something
6. Scheduling something
7. Buying or ordering something
8. Becoming something
9. Protecting something

Two intents have no GoA representation at the leverage-bar level:
- **Scheduling** — only ~4 candidate services (campsite reservation, road test, transportation booking).
- **Buying** — only EM-concentrated industrial buying (mineral rights, oil sands, emissions credits).

## The 14 service types

All pass the leverage bar. Sorted by primary task.

### Apply task (6 types)

| ID | Members | What it is |
|---|---|---|
| `apply-for-a-benefit` | 65 svc / 15 min | Eligibility, means test, decision letter, ongoing payments. _AISH, income support, student loans, childcare subsidy._ |
| `apply-for-a-grant-or-funding` | 51 svc / 17 min | Project-shaped: proposal, evaluation, contract, reporting. _FCSS funding, arts grants, Innovates funding._ |
| `apply-for-a-licence-or-permit` | 49 svc / 15 min | Demonstrate qualification, get credential with expiry. Includes the renewal sub-shape. _Driver's licence, firearms PAL, teacher certification, gaming licence._ |
| `register-something` | 23 svc / 13 min | Submit identifying info, get registry entry. _Birth registration, business registration, apprentice registration._ |
| `request-government-action-or-records` | 16 svc / 8 min | Formal request for records or specific government action. _FOI, fatality inquiry, victim impact statement._ |
| `appeal-a-decision` *(extension)* | 10 svc / 8 min | Reference a prior decision, submit grounds, await new decision. _Benefit appeals, court appeals, planning appeals._ |

### Transact task (1 type)

| ID | Members | What it is |
|---|---|---|
| `pay-a-fee-or-fine` | 6 svc / 4 min | Look up obligation, pay, receive receipt. _Traffic fines, fuel tax, mineral rights tax._ |

### Check task (1 type)

| ID | Members | What it is |
|---|---|---|
| `check-status-or-records` | 27 svc / 12 min | Authenticated lookup of own records, status, history. _Immigration status, health coverage, student loan account._ Likely needs a new `account` / `portal` productType in the design system. |

### Report task (2 types)

| ID | Members | What it is |
|---|---|---|
| `report-a-concern-or-incident` | 28 svc / 18 min | Push info about a hazard or third party. No assessment of the citizen's eligibility. _Child abuse, wildfire, animal disease._ |
| `file-a-complaint` | 20 svc / 12 min | Formal complaint about a regulated party, with investigation. _Health professional, employer, police conduct, business marketplace._ |

### Find task (3 types)

| ID | Members | What it is |
|---|---|---|
| `read-information-or-guidance` | 190 svc / 28 min | Content-shaped: guidance, rights, programs. Lowest design-system value because it's content/IA, not action — but ~30% of the corpus. |
| `search-a-public-register` | 25 svc / 17 min | Query a public registry to verify or retrieve. _Land titles, court records, drug coverage list, professional registration._ |
| `find-a-service-or-place` | 20 svc / 14 min | Find a provider, place, or service by location/criteria. _Family doctor, victim services, mental health support._ |

### Advise task (1 type)

| ID | Members | What it is |
|---|---|---|
| `access-an-in-person-program` | 69 svc / 11 min | Service exists but has no digital channel. Citizen finds, calls, or visits in person. **Surfaces a digital-readiness gap, not a design system gap.** |

## Cross-cutting gaps

Patterns missing from the design system that span multiple service types:

1. **Eligibility checking** before applying.
2. **Status tracking** after submission.
3. **Save and return** across sessions for long applications.
4. **Account/portal** — likely earns its own productType beyond `workspace` and `public-form`.
5. **Payment as a step** in a flow — likely earns its own productType.
6. **Notifications and follow-up** patterns.
7. **Decision letters** — current `result-page` example is too thin for the complexity of decisions.

## Coverage

- **637 supporting services** across 28 ministries classified by service task.
- **599 categorised** into 14 service types (94%).
- **38 uncategorised** edge cases — concentrated in JUS-only legal protection orders, EM-only industrial buying, scheduling-shape services, niche disputes. All genuinely below leverage bar.

## Methodological notes

- **Worker-side service types** (intake-and-assess, case management, the back-half of every service) are deferred to a follow-up. This analysis is citizen-side only.
- **Brief 12's product demo pattern data was deliberately deferred** from the analysis. Product demos can carry user-bias and broken designs that bias the system view. This analysis draws from the ministry maps directly and brings in patterns later as a connection layer, never a defining one.
- **Renewal** was tested as a separate service type but folded into `apply-for-a-licence-or-permit` as a sub-shape variation — only 4 genuine renewal services pass the leverage bar after de-contaminating program-name false matches like "Renewal Stream" or "renewal funding."

## What this enables

The analysis feeds into wiring the service map into the design system AI layer. Once wired, a team should be able to show up to the design system saying "I'm building for [the intake-and-assessment service at ALSS]" and get back:

- The service type and its shape
- Connections to existing docs site examples and components
- Gaps where new examples are worth building
- Patterns from across other ministries that share the same shape

## Files

- `service_types.json` — full structured analysis (the source of truth)
- `service_types.md` — this document
- Per-ministry maps in this folder (`acsw.json` through `ts.json`) — the corpus this analysis was derived from

## Working files

The analysis path lives in this repo at `analysis/service-types/`:
- `classify_by_task.py` — Phase 1: classify services by primary task using channel signals
- `phase-1-classification.json` — every service tagged with its primary task
- `cluster_within_task.py` + `phase-2-clusters-raw.md` — Phase 2: cluster within each task by name pattern
- `phase-2-clusters.md` — curated service-type definitions (snapshot from mid-analysis; see `service_types.json` for the current state)
- `phase-3-mappings.md` — per-type cross-references to design system docs site examples + productTypes + gaps + proposed examples
- `build_service_types.py` — Phase 4: builder that produces `service_types.json` from the matchers and hand-authored content
- `phase-4-uncategorised.txt` — the 38 edge cases left out
- `sample_buckets.py` — sampler for sanity-checking task buckets

Regenerate `service_types.json` by running `python3 build_service_types.py` from `analysis/service-types/` when ministry maps change materially.
