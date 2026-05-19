# Phase 5: Critical Pass on Brief 06 Outputs

Brief 08 working file. Critical second-pass review of the 14 service types in `service_types.json` and the cross-cutting gaps list. Goal: catch missed gaps, de-duplicate proposed examples across types, and prepare priority signals for Brief 07's wiring.

**Status (2026-05-19):** Phase 1-4 landed including the value-weighting layer. Artifact + MD summary regenerated. Hiro foundational catalog written. Brief 08 essentially complete; remaining: mirror to briefs/06-research/ if maintaining the duplication contract, then commit and push.

**What landed:**

- Cross-cutting gaps refactored from 7 → 10 entries. Renamed (`account-or-portal` → `my-account`, `payment-step` → `payment`, `notifications-and-follow-up` → `service-messages`). Decision-letters absorbed into a new parent `results` pattern with five variants (submission-receipt, decision-letter, issued-credential, records-release, appeal-outcome). Three new entries added (`submit-supporting-documents`, `describe-what-happened`, `look-up-and-pick`). Status-tracking gained a `flavors[]` array (one structural pattern, eight type-flavors).
- Per-type `gaps` and `proposed_examples` reshaped: each entry is now a dict (`text`/`concept` + optional `cross_cutting_refs` + optional `flavor_note` + `priority` + `priority_rationale`).
- Per-gap and per-proposed-example priority computed (leverage-only): mechanical signal of service-type weight × cross-cutting reach, with two subjective overrides (read-information-or-guidance and access-an-in-person-program forced to low).
- Four candidate new productTypes surfaced for joint commitment with Paul: `payment`, `account` / `portal`, `directory` (with two variations), `short-form`. Brief 08 deliberately did NOT bump these.
- `build_service_types.py` regenerated `service_types.json` as a working snapshot. Not committed.

**What's left:**

- Mirror `analysis/service-types/` and the data files back to `briefs/06-research/` if maintaining the working-space-vs-shared-snapshots duplication contract.
- Commit and push to `goa-service-maps` (data on `main`; build script changes via PR per the hybrid branch strategy).
- Mark Brief 08 ✅ Complete.

**Value-weighting framework landed:**

The priority signal is now layered. Mechanical leverage (service count + cross-cutting reach) computes the default. Value-weighting (curated across reach / financial / need / dependency) overrides where the partnership-level judgment says the mechanical signal undercounts. `priority_rationale` surfaces both reasons.

First-pass value-weighting curated by Tom on 2026-05-19. Refinable as data sources for citizen reach and financial flow become available, or as the partnership refines the four dimensions.

**Pipeline:** Phase 1 (re-read each type, surface observations) ✅ → Phase 2 (de-dup) ✅ → Phase 3 (priority ranking, leverage-only) ✅ → Phase 3.5 (value-weighting layer) ✅ → Phase 4 (write artifact + auto-generated summary + Hiro foundational catalog) ✅.

**Auto-sync pattern adopted:** `build_service_types.py` now outputs both `service_types.json` AND `service_types.md`. The MD is auto-synced with the JSON; do not hand-edit. The Hiro foundational doc (`hiro/memory/alberta-service-types-catalog.md`) is hand-curated and stable, references the live data via pointer.

---

## Phase 1: Per-type critical re-read

Each section lists: leverage stats, observations on gaps, observations on proposed examples, cross-type overlap, and any sharpening needed. Sorted by service task then by service count (high → low).

### Apply task

#### `apply-for-a-benefit` (65 svc / 15 min)

**Gaps**
- All 5 listed are real and well-formed.
- *Missing:* No "claim-shaped" eligibility variation. The `variations` note disaster recovery / wildlife damage as claim-shaped, but the gap list assumes means-tested or categorical. Event-triggered eligibility (prove loss, prove damage, prove event affected you) is structurally different and not covered.
- *Missing:* No "ongoing review / annual recertification" pattern. AISH, income support, childcare subsidy all require recertification. This is repeat-application, not first-time.

**Proposed examples**
- *Cross-cutting overlap:* "Eligibility checker" duplicates cross-cutting gap `eligibility-checking` (which also applies to licence, grant). Promote to cross-cutting; remove from per-type or downgrade to "see also."
- *Cross-cutting overlap:* "Status tracker" duplicates cross-cutting `status-tracking`. Promote.
- *Cross-cutting overlap:* "Save-and-return" duplicates cross-cutting `save-and-return`. Promote.
- "Means-test composer" is uniquely benefit-shaped. Keep per-type. Strong candidate for highest within-type priority.
- "Respond to a clarification request" is a strong specific pattern. Worth checking if it generalizes to licence (worker asks for more info on training docs) — possibly cross-cutting candidate.

#### `apply-for-a-grant-or-funding` (51 svc / 17 min)

**Gaps**
- All 5 listed are real, but two are *deferred*: reporting-back is worker-side. That leaves 4 active grant-specific gaps.
- *Missing:* No mention of eligibility-checking, save-and-return, status-tracking — even though cross-cutting list claims grants belong to all three. Either the cross-cutting list is wrong or per-type list is missing entries. **Most likely: the cross-cutting list is correct and per-type should reference, not restate. Same fix applies to all Apply types.**
- *Missing:* No "letter of support / endorsement" pattern. Grants commonly require third-party endorsements that aren't standard document uploads.

**Proposed examples**
- "Budget table input" — uniquely grant-shaped (itemized cost rows with categories). Keep per-type. High within-type priority.
- "Project team composer" — applies to grants strongly, also to licence (firearms applications list users, business permits list officers) and report (witnesses). Possible cross-cutting if it generalizes; keep per-type if it doesn't.
- "Document checklist with upload" — generalizes across grant, complaint, report, records-request. Strong cross-cutting promotion candidate.
- "Multi-organization profile" — uniquely grant/business-shaped. Keep per-type.

#### `apply-for-a-licence-or-permit` (49 svc / 15 min)

**Gaps**
- 7 listed (4 base + 3 renewal-specific). Real and well-formed.
- *Missing:* No "premises inspection / external evidence" pattern. Some licences (food premises, cannabis retail, security) require third-party inspection results before issuance.
- *Missing renewal-specific:* No "lapsed renewal" gap. What happens when the renewal window closed and the credential expired? Different shape from active renewal.

**Proposed examples**
- "Attestation / declaration" — applies to licence strongly but also to other Apply types (consent of truth on benefit applications, declarations on register-something). Possible cross-cutting candidate; lean keep-per-type because licence has the strongest case (under-penalty signature).
- "Qualifications composer" — uniquely licence-shaped. Keep per-type.
- "Pay-and-submit" — overlaps with cross-cutting `payment-step`. Promote or merge.
- "Issued credential page" — a *decision-letter variant* (cross-cutting `decision-letters`) with credential-specific affordances (print, wallet-add). Promote the structural pattern; keep the credential flavor per-type.
- "Verify-and-renew flow" — uniquely licence-renewal. Keep per-type. **This is one of the most concrete reusable artefacts in the whole list.**
- "Renewal reminder" — a *notification variant* (cross-cutting `notifications-and-follow-up`). Promote the notification pattern; keep the renewal flavor per-type.

#### `register-something` (23 svc / 13 min)

**Gaps**
- 3 listed, all well-formed.
- *Missing:* No "validation-without-eligibility" pattern. Registries do uniqueness/format checks (is this VIN already registered? is this business name available?) without full eligibility assessment. Distinct from `eligibility-checking`.
- *Missing:* No "expiry / renewal" pattern. Some registry entries expire (apprentice registration, professional registration) — overlap with licence renewal but not the same shape.

**Proposed examples**
- "Compact form page" — uniquely register-shaped (the structural counter to public-form's one-question-per-page assumption). Strong keep-per-type. **High candidate for cross-cutting promotion at the product-type level** — compact-form might earn its own productType.
- "Registry receipt" — a result-page variant (decision-letter cross-cutting territory). Could be a flavor.
- "Update an existing record" — overlaps with renewal in licence and with my-account in check-status. The "look up → modify → confirm" pattern is broader than register; possibly cross-cutting.

#### `request-government-action-or-records` (16 svc / 8 min)

**Gaps**
- 3 listed, all well-formed.
- *Missing:* No "fee-on-request" pattern despite many records requests being paid (court records, transcripts).
- *Missing:* No "third-party authorization" pattern. Some records requests require consent from the person whose records are being requested.

**Proposed examples**
- "Records request form" — uniquely shaped (checklist of required info before submission). Possible generalization to other formal-request shapes.
- "Request status with timeline" — duplicates cross-cutting `status-tracking` with the variation that legislated timelines are surfaced. The "legislated timeline" angle is distinct enough to keep flavored per-type while the structural pattern is cross-cutting.
- "Released records view" — uniquely this type. Keep per-type. **Includes the redaction-explanation sub-pattern which is rare.**

#### `appeal-a-decision` (10 svc / 8 min) `is_extension: true`

**Gaps**
- 4 listed. All well-formed.
- *Missing:* No "deadline to appeal" pattern. Most appeals have strict windows (30 days, 60 days) — citizens need to see this before starting.
- *Missing:* No "evidence packet upload" pattern for appeals, though "grounds composer" implies it.

**Proposed examples**
- "Appeal initiation" — uniquely appeal-shaped (load prior decision + select grounds). Keep per-type.
- "Appeal status" — duplicates `status-tracking` cross-cutting with the variation of appeal-specific milestones. Same treatment as records-request: cross-cutting structure with per-type content flavor.
- "Appeal outcome letter" — a decision-letter variant with three-branch outcomes (uphold/overturn/remit). Distinct enough to keep per-type but the structural pattern is `decision-letters`.

### Transact task

#### `pay-a-fee-or-fine` (6 svc / 4 min)

**Gaps**
- 4 listed. Real.
- The leverage stats are the lowest of any service type (6/4). Brief 06 already notes this type likely earns its own productType (`payment` / `transaction`).
- *Missing:* No "partial payment / payment plan" pattern. Some obligations can be paid in installments.

**Proposed examples**
- All 4 proposed are unique-to-payment and would compose a payment productType.
- "Account-balance view" — overlaps with `check-status-or-records` "History timeline" + "My-account home." When the future `account/portal` productType lands, this gets absorbed. For now, keep per-type with a note.

**Strategic:** The whole type's outputs feed Brief 07's argument for a new `payment` productType. The priority signal should mark this whole type as **structurally important despite low leverage** — the payment pattern is missing from the design system and shows up everywhere.

### Check task

#### `check-status-or-records` (27 svc / 12 min)

**Gaps**
- 4 listed. Real.
- *Missing:* No "delegated access" pattern. Some checks allow proxies (parent checks child's coverage, caregiver checks senior's benefits).

**Proposed examples**
- All three proposed are account/portal productType material. Brief 06 already notes this type likely earns its own productType.
- "Status with action affordance" gap overlaps strongly with cross-cutting `status-tracking`. The sharpening: status-tracking should explicitly include the "and now what?" affordance.

**Strategic:** Same as pay-a-fee-or-fine — this type's outputs feed Brief 07's argument for a new `account` or `portal` productType. Mark as **structurally important** even though service count is moderate.

### Report task

#### `report-a-concern-or-incident` (28 svc / 18 min)

**Gaps**
- 4 listed. Strong and unique.
- *Missing:* No "what counts as reportable" pattern. Many reports start with "should I report this?" guidance (child abuse, elder abuse, animal welfare).

**Proposed examples**
- "Optional-identity report form" — uniquely report-shaped. Keep per-type. **One of the most distinctive patterns in the corpus.**
- "Report receipt with reference number" — generalizes to many types (any submission needs a receipt). Cross-cutting candidate (receipts with reference numbers).
- "Evidence-attached-to-fact composer" — overlaps with grant's document checklist, complaint's evidence, records-request attachments. Cross-cutting candidate for evidence/document upload.

#### `file-a-complaint` (20 svc / 12 min)

**Gaps**
- 5 listed. Real. The fifth ("appeal-pathway pattern") is noted as overlapping with `appeal-a-decision` — already cross-referenced.
- *Missing:* No "without-prejudice / mediation" pattern. Some complaints route to mediation before formal investigation.

**Proposed examples**
- "Identify the regulated party" — generalizes to find-a-service, search-register, renewal look-up. Cross-cutting candidate (entity search-and-select).
- "Timeline-of-events composer" — could generalize to appeal (grounds with events), report (incident timeline). Cross-cutting candidate (narrative composer).
- "Investigation status updates" — cross-cutting `status-tracking` again. Same treatment.
- "Decision letter view" — cross-cutting `decision-letters`. Same treatment.

### Find task

#### `read-information-or-guidance` (190 svc / 28 min)

**Largest service count in the corpus, lowest design-system value.**

**Gaps**
- 3 listed. Reasonable.
- *Missing:* No "guidance + related programs" pattern (sidebar with related actions/programs).
- *Missing:* No "guidance with last-updated metadata" pattern (citizens need to know if rules content is current).

**Proposed examples**
- All three are reasonable. Low design-system priority because it's content/IA, not action.
- "Inline calculator" — overlaps with `eligibility-checker` cross-cutting (calculator-style). Could merge or cross-reference.

**Strategic:** Mark whole type as **LOW priority** despite high leverage. Brief 07's note already says "this category exists; the design system is action-shaped and does not yet differentiate offerings here." Priority should match.

#### `search-a-public-register` (25 svc / 17 min)

**Gaps**
- 3 listed. Real.
- *Missing:* No "subscribe to changes" pattern. Some registry watchers want notifications when entries change (land title alerts, professional discipline changes).

**Proposed examples**
- "Verification result" — uniquely register-shaped (yes/no with detail). Keep per-type.
- "Paid-record retrieval" — overlaps with cross-cutting `payment-step`. Promote payment-as-step; keep paid-record flavor per-type.
- "Citation-ready record view" — uniquely register-shaped. Keep per-type.

#### `find-a-service-or-place` (20 svc / 14 min)

**Gaps**
- 4 listed. Real.

**Proposed examples**
- All four are directory-shaped and form a coherent set. Strong candidate for a `directory` productType (already noted).
- "Empty state with recovery" — likely a cross-cutting *interaction* pattern, not service-type-specific (every search needs a no-results state). Possibly demote to interaction-example layer.

### Advise task

#### `access-an-in-person-program` (69 svc / 11 min)

**Gaps**
- 1 listed (the gap-is-the-type). Real.
- No proposed examples. Correct — there's nothing to build for design system because there's no digital surface.

**Strategic:** Mark whole type as **structurally informative but not actionable** in this analysis. Highest service count after read-information; pure signal-of-gap rather than design-system gap.

---

## Phase 2: De-duplication and cross-cutting proposals

### Promote to cross-cutting (already in cross-cutting list — sharpen and consolidate)

| Cross-cutting gap | Per-type duplicates to fold in | Action |
|---|---|---|
| `eligibility-checking` | benefit's "Eligibility checker" | Promote, remove from per-type or replace with "see also" |
| `status-tracking` | benefit's "Status tracker", appeal's "Appeal status", complaint's "Investigation status updates", records-request's "Request status with timeline" | Promote one structural pattern. Keep per-type *flavor* notes (legislated-timeline for FOI, three-branch for appeal, long-running for complaints, "and now what?" affordance for check) as variations of the structural pattern |
| `save-and-return` | benefit's "Save-and-return" | Promote, remove from per-type |
| `account-or-portal` | check-status's three proposed examples | Promote as productType; check-status proposed examples become exemplars of the productType |
| `payment-step` | licence's "Pay-and-submit", search-register's "Paid-record retrieval", pay-fee-or-fine's entire proposed set | Promote payment-step as composition pattern; pay-fee-or-fine type becomes the new productType anchor |
| `notifications-and-follow-up` | licence's "Renewal reminder", benefit's "Respond to a clarification request" landing | Promote; per-type kept as flavor variations |
| `decision-letters` | licence's "Issued credential page", complaint's "Decision letter view", appeal's "Appeal outcome letter", records-request's "Released records view", grant's implicit award letter | Promote structural pattern. Keep per-type *flavors* (credential, three-branch, long-form-reasoning, released-records-with-redactions) as variations |

### New cross-cutting candidates (not in current list)

These recur across 3+ types and look promotable:

1. **Receipt with reference number** — applies to register (registry receipt), report (report receipt), pay-fee (payment receipt), apply-* (implicit). Could merge into `decision-letters` as the receipt sub-pattern, OR earn its own. Lean: separate, because receipts are simpler than decision letters.

2. **Document / evidence upload with checklist** — applies to grant (document checklist), report (evidence composer), complaint (evidence), records-request (attachments). Currently no cross-cutting entry; should be added.

3. **Entity search-and-select** — applies to complaint (identify regulated party), find-place (directory), search-register (lookup), licence renewal (look up existing). Currently no cross-cutting entry.

4. **Narrative / timeline composer** — applies to complaint (timeline of events), appeal (grounds), report (incident description). Currently no cross-cutting entry.

5. **Lookup → action shape** — applies to check-status (status → action), pay-fee (lookup → pay), licence renewal (lookup → renew), update-existing-record. Possibly absorbed by `account-or-portal` productType but worth flagging.

### Merge / sharpen on existing items

- **`status-tracking`**: include "with action affordance" — current summary says "result-page covers immediate confirmation, not the long wait." Sharpen to add: "Status tracking must include 'and now what?' affordances when the citizen can act (apply for deferral, dispute, withdraw)."
- **`decision-letters`**: include the "branch outcomes" sub-pattern (appeal: uphold/overturn/remit; complaint: founded/unfounded/etc).
- **`payment-step` ↔ `pay-a-fee-or-fine`**: clarify that pay-fee-or-fine likely *is* a productType; the payment-step is the composition pattern for use inside other types. Two different artifacts.

### Keep per-type (genuinely distinct)

These should NOT be promoted; they're type-specific:

- benefit: "Means-test composer" (uniquely benefit math)
- grant: "Budget table input", "Multi-organization profile" (uniquely grant-shaped)
- licence: "Qualifications composer", "Verify-and-renew flow" (uniquely licence)
- register: "Compact form page", "Update an existing record" (uniquely register; compact-form might earn product-type-adjacent status)
- records-request: "Records request form" (formal-request checklist), "Released records view" (with redactions)
- appeal: "Appeal initiation" (load prior decision + grounds)
- complaint: (after promotion) the timeline composer remains, plus regulated-party search if not promoted
- report: "Optional-identity report form" (anonymity is uniquely report-shaped)
- check-status: keep as productType, examples are exemplars
- search-register: "Verification result", "Citation-ready record view"
- find-place: directory examples as productType exemplars
- pay-fee: examples as productType exemplars

---

## Phase 3: Priority ranking (preliminary)

Mechanical ranking inputs:

- **Service-type weight (S):** service_count buckets.
  - High (S=3): 50+ services (apply-for-a-benefit, apply-for-a-grant, access-an-in-person-program, read-information-or-guidance)
  - Medium (S=2): 20-49 services (licence, register, check-status, report, complaint, register-search, find-place)
  - Low (S=1): under 20 (request-records, appeal, pay-fee)
- **Gap reach (R):** number of service types affected.
  - High (R=3): cross-cutting gap, 4+ types
  - Medium (R=2): cross-cutting gap, 3 types OR cross-type pattern observed
  - Low (R=1): single type
- **Combined:** S+R into priority bucket.
  - Score 5-6 → **high**
  - Score 3-4 → **medium**
  - Score 1-2 → **low**
- **Subjective override (T):** Tom can promote/demote with a one-line rationale.

Open questions for Tom:

1. **`read-information-or-guidance` weighting:** Mechanically it's the highest-leverage type (190 svc). But Brief 06 explicitly notes lowest design-system value. Recommendation: subjective override to **low** with rationale: "Content-shaped; design system action surface doesn't differentiate this category." Confirm?

2. **`access-an-in-person-program` weighting:** 69 services but no digital channel. Recommendation: subjective override to **low** with rationale: "No digital surface to design for; the gap is digitization, not design system." Confirm?

3. **`pay-a-fee-or-fine` and `check-status-or-records` weighting:** Mechanically low/medium but structurally important (Brief 06 flags both for new productTypes). Recommendation: subjective override to **high** with rationale: "Earns a new productType; structurally underbuilt despite moderate leverage." Confirm?

4. **ALSS pilot tie-in:** Brief 09 will pick an ALSS service for the pilot. Should the matching service type get an extra priority bump now, or wait for Brief 09 to land and adjust then?

---

## Phase 4: Artifact updates (deferred until Phases 1-3 land with Tom)

When Tom confirms the Phase 2 dedup proposals and the Phase 3 priorities, regenerate `service_types.json` with:

- `priority` field (high/medium/low) on each `gap` and each `proposed_example`
- `priority_rationale` field with one-line reason
- `cross_cutting_gaps` updated (sharpened text, new entries for receipt / document-upload / entity-search / narrative-composer if accepted)
- `service_types[*].gaps` deduplicated (per-type entries that are now cross-cutting get a "see cross-cutting:<id>" pointer instead of restatement)
- `service_types[*].proposed_examples` deduplicated (same treatment)

Refresh `service_types.md` to surface high-priority entries first. Update `README.md` if methodology shifted.

Mirror updates to `briefs/06-research/` per the working-space-vs-shared-snapshots pattern.

---

## Open questions (capture surface)

1. **Per-type "see also" syntax**: how should per-type gap/proposed lists point at cross-cutting items without restating them? JSON field like `cross_cutting_refs: ["status-tracking"]`? Plain text "see also" in the entry? Schema decision affects Brief 07's wiring.

2. **Sub-pattern vs distinct pattern**: status-tracking has type-specific flavors (FOI 30-day, appeal three-branch, complaint long-running). Are those *variations* of one pattern or *distinct* patterns? Affects whether Brief 07 surfaces one example with variations or four examples.

3. **Receipt vs decision letter**: separate cross-cutting entries or merge under decision-letters? Two opinions, lean toward separate (receipts are confirmation; decision letters carry outcomes).

4. **Compact form**: Does register-something's "compact form page" earn a productType-adjacent designation, or stay as a public-form variation?
