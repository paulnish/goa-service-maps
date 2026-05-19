<!--
AUTO-GENERATED. Do not edit by hand.
Regenerate with: cd analysis/service-types && python3 build_service_types.py
Edit the build script (or its inputs), not this file.
-->

# Alberta service types

Generated 2026-05-19 from the ministry maps in this repo. The structured data lives next to this file in `service_types.json`; this doc is the readable summary.

## What this is

For any given service in Alberta, this analysis answers: what kind of service is it in the design-system / shape sense? Which other services across ministries share its shape? Which patterns and components down the design-system stack are reachable from it?

A **service type** is a `(service task × Kate Tarling intent)` cluster validated by a leverage bar (5+ services across 3+ ministries). It's the most stable thing about a service — channels and legislation change, the type rarely does.

## How priority is computed

Each service type, gap, and proposed example carries a `priority` field (high / medium / low) layered from two signals:

- **Mechanical leverage** — service-type weight (services in the type) or cross-cutting reach (types sharing this gap). Defensible from data alone.
- **Value-weighting** — curated using four dimensions: reach (citizens), financial flow, need / hurt, dependency / levers.

When value-weighting is set, it overrides the mechanical default. The `priority_rationale` field surfaces both reasons so the override is visible.

## Service tasks

Seven shapes describing how the citizen interacts:

| Task | What the citizen does |
|---|---|
| **Apply** | Demonstrates eligibility, submits, waits for a decision |
| **Transact** | Pays, renews, files, buys — completes a routine exchange |
| **Check** | Looks up status, records, history (authenticated to themselves) |
| **Report** | Pushes information about a hazard or third party |
| **Engage** | Participates in a consultation or decision process |
| **Find** | Looks up information, services, or providers |
| **Advise** | Gets human-mediated help; no digital action surface today |

## The service types, sorted by priority

### High priority (9)

| ID | Task | Members | Shape | Value-weight reasoning |
|---|---|---|---|---|
| `apply-for-a-benefit` | Apply | 65 svc / 15 min | Citizen demonstrates eligibility (means-tested or categorical), provides personal/household info, uploads supporting documents, waits for adjudication, receives ongoing or one-time payment with a decision letter. | Reach: hundreds of thousands of Albertans (income support, AISH, childcare subsidy). Financial: billions/year paid. Need: people depend on these to live. |
| `apply-for-a-grant-or-funding` | Apply | 51 svc / 17 min | Organization or project lead submits a proposal with budget, work plan, and outcomes; reviewed against program criteria; awarded with a contract or transfer payment agreement; ongoing reporting and accountability. | Financial: hundreds of millions to billions/year. Reach: medium (more orgs than individuals). |
| `apply-for-a-licence-or-permit` | Apply | 49 svc / 15 min | Citizen or business demonstrates qualification (training, fitness, fee paid, premises inspected), submits application with evidence, waits for decision, receives credential with expiry and conditions. | Reach: high (driver's licences alone touch millions; plus professional, business, activity permits). Need: high (daily-life-critical credentials). |
| `report-a-concern-or-incident` | Report | 28 svc / 18 min | Citizen pushes information about a hazard, suspected harm, or third-party concern. | Need: safety-critical (child abuse, wildfire, animal disease reports). Downstream costs of unreported incidents are high. |
| `check-status-or-records` | Check | 27 svc / 12 min | Authenticated citizen looks up their own status, account, history, or records held by government. | Reach: every benefit recipient, every licence holder, every student loan borrower. Anchors the account/portal productType candidate. |
| `search-a-public-register` | Find | 25 svc / 17 min | Citizen queries a public registry to verify a fact, find a record, or check status. | Reach: high (land titles, court records used heavily by businesses, lawyers, citizens). Anchors the registry-search variation of the directory productType candidate. |
| `register-something` | Apply | 23 svc / 13 min | Citizen or business submits identifying information, system validates basic eligibility (no full assessment), registry entry created, confirmation issued with a registration number. | Reach: high (vehicle, business, birth, marriage registrations). Need: high (required for daily life). Anchors the short-form productType candidate. |
| `find-a-service-or-place` | Find | 20 svc / 14 min | Citizen searches by location and need, gets a directory of providers/places with contact info, hours, eligibility hints. | Reach: every citizen who needs help finding a service. Need: people often in crisis (doctors, victim services, mental health). Anchors the provider-directory variation of the di... |
| `pay-a-fee-or-fine` | Transact | 6 svc / 4 min | Citizen receives or knows about an obligation (fine, fee, tax owed), looks up the amount, pays online with optional dispute path. | Financial: billions/year (traffic fines, fuel tax, royalties). Reach: high (every fueling, every fine). Anchors the payment productType candidate. |

### Medium priority (3)

| ID | Task | Members | Shape | Value-weight reasoning |
|---|---|---|---|---|
| `file-a-complaint` | Report | 20 svc / 12 min | Citizen files a formal complaint about a regulated party (professional, business, government decision-maker). | Reach: medium. Need: regulatory accountability matters but not life-or-death. |
| `request-government-action-or-records` | Apply | 16 svc / 8 min | Citizen submits a formal request for government records, information, or specific action (inquiry, mediation, restitution, impact statement). | Reach: medium (thousands of FOI requests, lawyer reviews per year). Need: democratic accountability and personal records access. |
| `appeal-a-decision` | Apply | 10 svc / 8 min | Citizen references a prior decision they want overturned, submits grounds (procedural error, new evidence, wrong on the merits), waits for review by a separate body, receives a new decision (uphold, overturn, or remit). | Reach: low but high need when invoked. Citizens' safety net when initial decisions go wrong. |

### Low priority (2)

| ID | Task | Members | Shape | Value-weight reasoning |
|---|---|---|---|---|
| `read-information-or-guidance` | Find | 190 svc / 28 min | Citizen consumes content explaining a topic, regulation, right, or program. | Content not action. Design system action surface doesn't differentiate this category regardless of value-weighting. |
| `access-an-in-person-program` | Advise | 69 svc / 11 min | Service exists but has no digital channel — citizen finds the program, calls or visits in person, gets human-mediated intake, receives the service. | No digital surface to design for. The gap is digitization, not design system. Value-weighting can't change that for this analysis. |

## Cross-cutting patterns, sorted by priority

Patterns that recur across multiple service types. Each per-type gap or proposed example that maps to one of these carries a `cross_cutting_refs` pointer in the JSON.

### High priority (9)

| ID | Applies to | Summary | Value-weight reasoning |
|---|---|---|---|
| `results` | 9 types | One parent pattern (what happened, what's next, contact path) with content variants based on what the result is. | Reach: every service interaction ends in a result page of some kind. Five content variants cover decision letters, credentials, records release, appeal outcomes, submission rece... |
| `status-tracking` | 8 types | One structural pattern (where is my thing in its journey, what's expected, what can I act on) with per-type content flavors. | Reach: every applicant. Spans benefits, licences, grants, appeals, complaints, records requests. High frustration relief on long waits. |
| `submit-supporting-documents` | 6 types | Multi-document checklist with upload status. | Reach: high. Common in grant applications, reports, complaints, records requests, benefit applications, licence applications. High friction point when not handled well. |
| `my-account` | 5 types | Authenticated home where citizens see their stuff (applications, status, history, records) and act on it (renew, dispute, download). | Reach: every authenticated citizen. Anchors the account/portal productType candidate. |
| `service-messages` | 5 types | Emails, texts, in-app messages government sends citizens when state changes (we received it, we need more info, your decision is ready, your licence expires in 30 days). | Reach: every applicant receives at least one. Decision letters, renewal reminders, clarification requests, status updates. |
| `look-up-and-pick` | 4 types | Embedded entity lookup as a step inside another flow: find the doctor you're complaining about, look up your existing licence to renew, identify the regulated party. | Sub-pattern but widely embedded. Useful in complaints, renewals, reports, find-place flows. |
| `eligibility-checking` | 3 types | Citizens need to know if they qualify before starting an application. | Reach: everyone who considers applying asks this first. High frustration relief. |
| `save-and-return` | 3 types | Long applications can't be done in one sitting; the public-form template assumes one session. | Reach: anyone filling a long form. Means-tested benefit applications run 30-60 minutes; many citizens can't finish in one sitting. |
| `payment` | 3 types | Pay an amount as part of a service interaction. | Financial: billions/year. Includes traffic fines, fuel tax, paid registry searches, licence application fees. |

### Medium priority (1)

| ID | Applies to | Summary | Value-weight reasoning |
|---|---|---|---|
| `describe-what-happened` | 3 types | Structured event-sequence input where the citizen recounts a sequence of events. | Bounded volume (complaints, appeals, reports). Important for accuracy but not high-reach. |

## Coverage

- **599 services** classified into 14 service types across 28 Alberta ministries.
- ~38 uncategorised edge cases — concentrated in JUS-only legal protection orders, EM-only industrial buying, scheduling-shape services, niche disputes. All below the leverage bar.

## Methodology

phase-1-classification of 637 supporting services by primary service task (channel-based with name-pattern overrides), then phase-2 clustering by name pattern within each task with leverage bar applied. A critical-pass dedup followed: per-type gaps and proposed_examples that duplicate cross-cutting patterns now carry cross_cutting_refs and flavor_note fields. Priority is computed from two layered signals — mechanical (service-type weight or cross-cutting reach) and value-weighting (curated per type and per cross-cutting using reach, financial flow, need, dependency). When value_weight is set, it overrides the mechanical default and the rationale surfaces both reasons.

**Constraints:**

- Citizen-side only. Worker-side service types (intake-and-assess, case management) deferred to a follow-up brief.
- Product demo patterns NOT used as input to avoid biasing the system view.
- Size-agnostic example proposals — captures the concept rather than the size class.
- Value-weighting is a first-pass curation (Tom 2026-05-19, with input from Paul). Refinable as data sources for citizen reach and financial flow become available.
- ALSS pilot tie-in not applied — pilot service pick happening over the next two weeks; matching service type's priority_rationale gets a targeted amendment once known.

## Files

- `service_types.json` — full structured analysis (the source of truth, including per-type gaps, proposed examples, services, and priority rationales).
- `service_types.md` — this document (auto-generated from the JSON).
- `analysis/service-types/` — build pipeline scripts and working notes.
