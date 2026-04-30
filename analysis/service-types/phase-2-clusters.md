# Phase 2 — Curated Service Types

Source data: `phase-1-classification.json` (637 supporting services across 28 Alberta ministries) and `phase-2-clusters-raw.md` (regex-derived candidate clusters).

This document is the curated layer. Each service type below is a `(service task × Kate Tarling intent)` cluster validated by the leverage bar (5+ services across 3+ ministries). Where the data didn't fit a Kate Tarling intent cleanly, it's flagged.

Final count: **13 service types** in scope; 3 borderline candidates noted; 1 explicit gap.

## Kate Tarling intent IDs (used below)

Per `goa-service-maps/.claude/skills/service-map-collector/references/service-types-future.md`:

| ID | Label |
|---|---|
| `registering-information` | Registering, providing or reporting information |
| `checking-information` | Requesting, sharing or checking information |
| `paying` | Paying for something |
| `financial-support` | Getting financial support or claiming something |
| `permission` | Getting permission to do something |
| `scheduling` | Scheduling something |
| `buying` | Buying or ordering something |
| `becoming` | Becoming something |
| `protecting` | Protecting something |

---

## Service types

### 1. `apply-for-a-benefit`

**Service task:** Apply • **Intents:** `financial-support`
**Leverage:** ~30 services across 9+ ministries (ALSS, SCSS, AE, EDU, AU, JUS, HEALTH, PPHS, IM)
**Shared shape:** Citizen demonstrates eligibility (means-tested or categorical), provides personal/household info, uploads supporting documents, waits for adjudication, receives ongoing or one-time payment with a decision letter. Some have ongoing review cycles.
**Variations:** Means-tested (income support, AISH, childcare subsidy) vs. categorical (seniors financial assistance, disability benefits). Some pay monthly, some are one-time. Some are loans (must be repaid), some are grants/subsidies.
**Representative services:**
- [alss] Get income, health and other benefits for a severe disability (AISH)
- [ae] Apply for Alberta student loans and grants
- [edu] Apply for child care subsidies
- [scss] Get monthly financial support as a senior
- [jus] Apply for the Escaping Abuse Benefit

### 2. `apply-for-a-grant-or-funding`

**Service task:** Apply • **Intents:** `financial-support`
**Leverage:** 26 services across 12 ministries
**Shared shape:** Organization or project lead submits a proposal with budget, work plan, and outcomes; reviewed against program criteria; awarded with a contract or transfer payment agreement; ongoing reporting and accountability.
**Variations:** Project grants (one-time, defined deliverables) vs. operating grants (ongoing, organizational support) vs. capital funding (infrastructure). Some are open-call competitive, some are formula-based.
**Representative services:**
- [tec] Apply for water and wastewater infrastructure funding
- [acsw] Apply for a community facility improvement grant
- [ts] Apply for a major sport events grant
- [ti] Apply for Alberta Innovates research or commercialization funding
- [ag] Apply for a beginning farmer loan

### 3. `apply-for-a-licence-or-permit`

**Service task:** Apply • **Intents:** `permission`
**Leverage:** ~25 services across 12+ ministries (combined apply-for-a-licence + apply-for-a-permit + get-a-licence-or-permit + scattered in apply-other)
**Shared shape:** Citizen or business demonstrates qualification (training, fitness, fee paid, premises inspected), submits application with evidence, waits for decision, receives credential with expiry and conditions. Renewal triggers a lighter version of the same shape.
**Variations:** Personal credentials (driver's licence, firearms PAL, professional licences) vs. business credentials (cannabis, security, locksmith) vs. activity permits (timber, fire, oversize load). Some require ongoing compliance and audit.
**Representative services:**
- [tec] Get a permit for an oversized or overweight load
- [jus] Apply for a Possession and Acquisition Licence (PAL)
- [tbf] Apply for or renew a gaming, liquor, or cannabis licence
- [edu] Apply for teacher certification
- [epa] Apply for a water licence or approval

### 4. `register-something`

**Service task:** Apply • **Intents:** `registering-information`, `becoming` (multi-intent: registering a business is registering-info; registering as an apprentice is becoming)
**Leverage:** ~19 services across 15+ ministries
**Shared shape:** Citizen or business submits identifying information, system validates basic eligibility (no full assessment), registry entry created, confirmation issued with registration number. Often ongoing — registry must be kept current.
**Variations:** Vital records (birth, marriage, death) vs. property records (vehicle, land, lien) vs. credentials (apprentice, regulated professional) vs. business identity (corporation, tourism levy collector). The "becoming" variants involve a person changing professional status; the others are filing facts about things.
**Representative services:**
- [sa] Register a birth or get a birth certificate
- [sa] Register a business name or corporation in Alberta
- [ae] Register as an apprentice
- [hshs] Register as an organ and tissue donor
- [tec] Register, renew, or transfer a vehicle

### 5. `pay-a-fee-or-fine`

**Service task:** Transact • **Intents:** `paying`
**Leverage:** 6+ services across 4+ ministries (combining pay-cluster + Transact-other entries like fuel tax, mineral rights tax)
**Shared shape:** Citizen receives or knows about an obligation (fine, fee, tax owed), looks up the amount, pays online with optional dispute path. Receipt issued; account updated.
**Variations:** Penalties (traffic fines, impaired driving) vs. recurring payments (fuel tax, mineral rights tax) vs. one-off fees (court filing fee, royalty payments). Dispute mechanisms vary.
**Representative services:**
- [tec] Pay a traffic fine
- [jus] Pay or dispute an impaired driving penalty through SafeRoads Alberta
- [em] Pay freehold mineral rights tax
- [tbf] File and pay fuel tax, tobacco tax, or tourism levy
- [jus] Pay or dispute a traffic ticket

### 6. `renew-something`

**Service task:** Transact • **Intents:** `permission` (renewal of permission held)
**Leverage:** ~7 services across 5+ ministries (combining Transact renew-cluster + Apply-side "or renew" services)
**Shared shape:** Holder confirms identity, system verifies eligibility hasn't lapsed (no medical change, no compliance breach), pays renewal fee, receives updated credential with new expiry.
**Variations:** Auto-eligible renewal (driver's licence, vehicle reg) vs. fitness-recheck renewal (firearms, regulated professional) vs. business renewal (gaming/liquor/cannabis). Some bundled with annual reporting.
**Representative services:**
- [tec] Renew or replace a driver's licence
- [jus] Renew a firearms licence
- [sa] Register or renew your vehicle registration
- [tbf] Apply for or renew a gaming, liquor, or cannabis licence
- [tec] Sign up for renewal reminders

### 7. `check-status-or-records`

**Service task:** Check • **Intents:** `checking-information`
**Leverage:** ~12 services across 9+ ministries (combining check-status + access-records-or-data + manage-account)
**Shared shape:** Authenticated citizen looks up their own status, account, history, or records held by government. Often the back-half of an Apply or Transact flow (status of an application; loan balance after applying for a loan).
**Variations:** Status checks (immigration application, health coverage) vs. account management (student loan, support payments) vs. personal records (health records). Some are anonymous status checks (wildfire status, fire bans), but those overlap with `find-a-service-or-place`.
**Representative services:**
- [im] Check your immigration application status
- [health] Check your health coverage status or claim history
- [ae] Manage your student loan
- [pphs] Access your personal health records online
- [jus] Track and manage your support payments online

### 8. `report-a-concern-or-incident`

**Service task:** Report • **Intents:** `protecting`
**Leverage:** ~24 services across 13+ ministries
**Shared shape:** Citizen pushes information about a hazard, suspected harm, or third-party concern. No assessment of the citizen's eligibility — the service is the act of reporting. Acknowledgment is usually sent; investigation may follow with no further citizen involvement, or follow-up may request more info.
**Variations:** Safety hazards (road, fire, wildlife) vs. abuse/harm reports (child, elder, workplace) vs. environmental incidents (substance release, emissions exceedance) vs. property/maintenance (government building issues). Some are time-critical (animal disease, wildfire).
**Representative services:**
- [cfs] Report concerns about child abuse or neglect
- [fp] Report a wildfire
- [jeti] Report a workplace health or safety concern or incident
- [ag] Report a suspected animal disease
- [tec] Report a road hazard or safety concern

### 9. `file-a-complaint`

**Service task:** Report • **Intents:** `protecting`
**Leverage:** 14 services across 11 ministries
**Shared shape:** Citizen files a formal complaint about a regulated party (professional, business, government decision-maker). Triage and acceptance, investigation by the regulator, decision communicated, possible appeal path. The complainant is heard but doesn't drive the process.
**Variations:** Regulated profession complaints (health, security, locksmith) vs. business marketplace complaints (consumer protection) vs. systemic complaints (human rights, police conduct, privacy) vs. specific party (guardian/trustee). Investigation rigour varies enormously.
**Representative services:**
- [health] File a complaint about a regulated health professional
- [im] File a human rights complaint about discrimination
- [pses] File a complaint about police conduct
- [sa] File a complaint about a business or marketplace issue
- [jeti] File a complaint about unpaid wages, wrongful termination, or other employment standards violations

### 10. `find-a-service-or-place`

**Service task:** Find • **Intents:** `checking-information`
**Leverage:** 14 services across 10 ministries
**Shared shape:** Citizen searches by location and need, gets a directory of providers/places with contact info, hours, eligibility hints. Often the front-half of an Advise or Apply flow — finding a provider is step 0 of getting help.
**Variations:** Health providers (doctors, treatment, hospitals) vs. social supports (settlement services, victim services, mental health) vs. physical places (libraries, parks, government offices) vs. regulated providers (forestry professional, addiction treatment).
**Representative services:**
- [health] Find a family doctor or primary care provider
- [pses] Find victim services in your community
- [mha] Find community mental health services near you
- [im] Find settlement services and newcomer supports in your community
- [ti] Find government services online

### 11. `search-a-public-register`

**Service task:** Find (and Transact for paid registers) • **Intents:** `checking-information`
**Leverage:** ~22 services across 15+ ministries (combining search-database-or-records + look-up-something + check-availability-or-status)
**Shared shape:** Citizen queries a public registry to verify a fact, find a record, or check status. May be free (most) or paid (court records, land titles). Citizen knows what they're looking for; result is a record or "no record found."
**Variations:** Validation queries (is this professional registered?) vs. record retrieval (land title, court record) vs. lookup-and-decide (is this drug covered? is broadband available here? is my child's school accredited?). Some require authenticated access, most are public.
**Representative services:**
- [pphs] Verify a health professional's registration status
- [pphs] Look up whether a drug is covered on the Alberta Drug Benefit List
- [jus] Search land title records online
- [ma] Look up your property assessment
- [edu] Search for licensed child care

### 12. `read-information-or-guidance`

**Service task:** Find • **Intents:** `checking-information`
**Leverage:** ~80 services across 20+ ministries (combining find-information-or-resource + read-or-access-information + learn-about + get-information-or-help)
**Shared shape:** Citizen consumes content explaining a topic, regulation, right, or program. No personalization; published guidance for general audiences. Often the only digital surface for non-digitized programs.
**Variations:** Rights/regulation content (employment standards, human rights) vs. program awareness (recycling, FireSmart, broadband) vs. data and statistics (economic data, environmental data) vs. how-to guides (caregiving, mental health support). Quality and depth vary widely. **Design-system relevance is lower** for this type — much of it is content/IA territory rather than action design — but it's still 12% of the corpus and Brief 07 needs to surface it for completeness.
**Representative services:**
- [jeti] Learn about minimum wage, hours of work, overtime, and leave entitlements
- [epa] Access air quality data and monitoring reports
- [im] Learn about human rights protections and anti-racism resources
- [tbf] Find information about insurance regulation and your rights
- [cpe] Subscribe to government news and topic alerts

### 13. `access-an-in-person-program`

**Service task:** Advise • **Intents:** `financial-support`, `protecting` (multi-intent depending on program)
**Leverage:** ~20 services across 5+ ministries (combining access-a-program-or-service + get-emergency-or-crisis-support)
**Shared shape:** Service exists but has no digital channel — citizen finds the program, calls or visits in person, gets human-mediated intake, receives the service. The digital surface (if any) is `find-a-service-or-place` shaped pointing at the program.
**Variations:** Emergency/crisis services (shelter, evacuation support, crisis lines) vs. specialized in-person supports (food bank, addiction treatment, brain injury). All concentrated in ALSS/SCSS plus MHA, JUS, CFS.
**Why this matters for the design system:** This category is the explicit non-digital gap. ~11% of Alberta services live here. The design system can't help build a citizen-facing application for these — there isn't one yet. Brief 07 should surface this so teams considering digitization see what's already in flight (or not) across ministries. The leverage bar for *digitizing* this category is high; the design system's role is forward-looking.
**Representative services:**
- [alss] Access emergency or transitional shelter
- [scss] Access food bank services
- [alss] Get emergency financial assistance
- [jus] Get emergency legal advice while in custody
- [mha] Access addiction treatment or detoxification services

---

## Borderline candidates (not in the main list)

### A. `submit-a-claim` (variant of apply-for-a-benefit, claim-shaped)

**Reason for not splitting out:** The shape is close enough to `apply-for-a-benefit` that splitting adds complexity without leverage. Members include "File a wildlife damage compensation claim", "File a claim under the new home warranty program", "Apply for disaster recovery assistance", "Claim jury duty expenses". Distinct sub-shape: triggered by a real-world event (damage, disaster, court appearance) rather than ongoing eligibility. **Surface as a variation note inside `apply-for-a-benefit`** rather than a separate type.

### B. `appeal-a-decision` (extension to Kate Tarling's nine)

**Why surfaced:** Multiple ministries have explicit "Appeal a..." services — appeal a benefit decision (ALSS, SCSS), appeal a municipal planning decision (MA), appeal a safety codes decision (MA), appeal a police complaint decision (PSES), appeal a court decision (JUS). ~6-8 services across 5+ ministries. Passes leverage bar.

**Why borderline:** Kate Tarling's nine treats appeals as part of the underlying service rather than a standalone type. The data argues otherwise — appeals have a recognisable shape (request review, submit grounds, reconsideration or hearing, new decision) that's not just "Apply again." **Recommend including as a 14th type in the final artifact** and flagging as an extension to the Kate Tarling vocabulary, with evidence.

### C. `engage-in-consultation`

**Reason below leverage bar:** Only 4 services across 3 ministries. The data isn't there yet. Worth re-checking when CPE adds more consultation services or another jurisdiction is added. **Flag as a known gap, not a service type.**

---

## Tasks not represented as standalone service types

| Task | Why no service type from this task |
|---|---|
| `Engage` (4 services) | Below leverage bar; surface as a known gap. |
| `Unclassified` (3 services) | Too few and too varied (AQHI app, alerts subscription, supervised consumption); would not pass leverage bar even consolidated. |
| `No-channels` (0 services) | Empty bucket. |

---

## Multi-intent tagging (for the schema)

A few service types genuinely span multiple Kate Tarling intents and should be tagged with multiple parents:

- `register-something` → `registering-information` + `becoming` (apprentice/professional registrations are becoming-shaped; vehicle/business/birth registrations are registering-information)
- `apply-for-a-licence-or-permit` → `permission` (primary) + `becoming` (secondary, for personal credentials like teacher certification or PAL)
- `access-an-in-person-program` → `financial-support` (emergency $) + `protecting` (shelter, crisis support) — varies by program

---

## Coverage check (Kate Tarling vs. data)

| Kate Tarling intent | Service types tagged with it | Coverage |
|---|---|---|
| `registering-information` | register-something | ✅ |
| `checking-information` | check-status-or-records, find-a-service-or-place, search-a-public-register, read-information-or-guidance | ✅ (heavily used) |
| `paying` | pay-a-fee-or-fine | ✅ |
| `financial-support` | apply-for-a-benefit, apply-for-a-grant-or-funding, access-an-in-person-program | ✅ |
| `permission` | apply-for-a-licence-or-permit, renew-something | ✅ |
| `scheduling` | (none) | ❌ — gap |
| `buying` | (none, but bordered by `pay-a-fee-or-fine` for industrial buying) | ❌ — small data; em-only |
| `becoming` | register-something, apply-for-a-licence-or-permit | ✅ (multi-tag) |
| `protecting` | report-a-concern-or-incident, file-a-complaint, access-an-in-person-program | ✅ |

**Two Kate Tarling intents have no GoA representation:**
- `scheduling` (booking appointments, prison visits) — Alberta has things like "Reserve a campsite" (1 service), "Book and take a road test" (1 service), "Book community transportation" (2 services). 4 services total, ~3 ministries. **Marginal pass on leverage bar; flag as a 15th type candidate** if the count holds up under recheck.
- `buying` — only EM-concentrated (mineral rights, oil sands, emissions credits). ~7 services in 1-2 ministries. Below leverage bar by ministry spread. **Flag as Alberta-specific gap; not a type.**

---

## What this means for Phase 3 and 4

**Final service-type list to wire up in Phase 4 schema:**

13 main types + 1 extension (`appeal-a-decision`) = **14 service types**.

Plus `book-or-schedule-something` (scheduling) as a candidate-15th if it survives a recount in Phase 4 verification.

Plus 2 explicit gaps surfaced in the artifact:
- `engage-in-consultation` (below leverage; data not ready)
- `buy-or-acquire-rights` (Alberta-concentrated in EM)

Phase 3 takes these 14 types into the docs site cross-reference: which existing examples already serve each, which gaps are real, what new examples are worth proposing.
