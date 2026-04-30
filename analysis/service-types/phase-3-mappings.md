# Phase 3 — Service Type to Docs Site Mappings

For each service type from `phase-2-clusters.md`, this doc maps down to:
- **productType** assignment (workspace, public-form, both, or neither — citizen-side only per scope).
- **Existing examples** on the docs site that apply (page-scale, interaction-scale).
- **Gaps** — what's missing in docs that would make this service type usable as a starting point.
- **Proposed new examples** — size-agnostic per Tom's instruction; capture the concept.

References the docs site state assuming **PR #3888 has merged** (productTypes collection live; workspace and public-form as productTypes; question-page consolidated; error-pages overview live; aliases-driven redirects).

Examples paths use shortened slugs (`/examples/{slug}` form). Workspace pages are `workspace/{slug}` post-PR; public-form pages are `public-form/{slug}` post-PR.

Examples are referenced by slug at the page-scale member level. For interaction-scale snippets I list categories rather than enumerating all 60+.

---

## 1. `apply-for-a-benefit`

**ProductTypes used:** `public-form` (citizen side).
**Existing examples (page-scale):** `public-form/start-page`, `public-form/task-list-page`, `public-form/question-page` (with all 6 question variants), `public-form/review-page`, `public-form/result-page`.
**Existing examples (interaction-scale):** `ask-a-user-for-an-address`, `ask-a-user-for-a-birthday`, `ask-a-user-for-direct-deposit-information`, `ask-a-user-for-an-indian-registration-number`, `ask-a-user-for-dollar-amounts`, `expand-or-collapse-part-of-a-form`, `reveal-input-based-on-a-selection`, `form-stepper-with-controlled-navigation`, `show-a-user-progress` and `show-a-user-progress-when-the-time-is-unknown`, `link-the-user-to-give-feedback-to-the-service`.

**Gaps:**
1. No eligibility-check pattern (Phase 1-2 of the Apply six-phase flow). Citizens often need to know if they qualify before starting an application; today there's no canonical example of "answer 4-5 questions, get a yes/no/maybe with reasons."
2. No means-test screen — most Alberta benefits are means-tested (income/asset thresholds), but no example shows how to handle the income+household+deductions math in a form.
3. No status-tracking page (Phase 5 of the flow). Once the citizen submits, they wait. The current `result-page` example covers the immediate confirmation; nothing covers "check on a long-running decision later."
4. No clarification-request flow. When the worker side asks for more info, the citizen needs to respond — that's a coupled patternless touchpoint.
5. No save-and-return pattern. Means-tested applications are long; many citizens can't finish in one sitting. The public-form template assumes one session.

**Proposed new examples (size-agnostic, by concept):**
- **Eligibility checker.** A short pre-form that gates the main application. Could be a single page or a 3-step mini-flow.
- **Status tracker.** Page citizens visit after submitting to see where their application is. Probably page-scale; could be embedded in a workspace-style portal.
- **Means-test composer.** Section or page that handles the eligibility math (income, household, deductions) with explanatory help.
- **Save-and-return.** Pattern for partial-fill state across sessions. Likely interaction or section scale plus account-side pages.
- **Respond to a clarification request.** Page or flow that the citizen reaches via email/notification, lets them upload more info or answer follow-up questions.

---

## 2. `apply-for-a-grant-or-funding`

**ProductTypes used:** `public-form` (citizen side, but with project-shaped questions rather than person-shaped).
**Existing examples (page-scale):** Same as above — `public-form/*` family, `result-page`, `review-page`.
**Existing examples (interaction-scale):** `ask-a-user-for-dollar-amounts`, `expand-or-collapse-part-of-a-form` (relevant for budget breakdowns), `add-another-item-in-a-modal` (multi-item lists like board members or sub-projects), `add-a-record-using-a-drawer`.

**Gaps:**
1. No project-budget input pattern. Grant applications need structured cost tables (line items, sub-totals, requested vs. matched). No example captures this.
2. No multi-applicant/team pattern. Grants often need lists of project participants, board members, or partners with their own info each.
3. No work-plan/milestone composer. Grants ask for project timelines and deliverables.
4. No attachment manager. Grant applications often require multiple supporting documents (financials, references, project plans) — current `ask-a-user-for-*` examples don't cover document upload at scale.
5. No reporting-back flow (post-award). The Apply six-phase flow's phase 6 for grants extends into ongoing project reporting, which is a workspace-shaped activity but no template exists.

**Proposed new examples:**
- **Budget table input.** Section-scale composer with itemized rows, categories, totals.
- **Project team composer.** Pattern for adding multiple participants with their own form fields each.
- **Document checklist with upload.** Page-scale or section pattern showing required attachments with status indicators.
- **Grant reporting page.** Workspace-side page (worker scope, deferred to follow-up brief) where grantees report back.
- **Multi-organization profile.** Section pattern for the org submitting (their address, registration, history).

---

## 3. `apply-for-a-licence-or-permit`

**ProductTypes used:** `public-form` (citizen side, sometimes paired with workspace for issuance/audit but worker scope deferred).
**Existing examples (page-scale):** `public-form/*` family, `start-page`, `task-list-page`, `question-page`, `review-page`, `result-page`.
**Existing examples (interaction-scale):** `ask-a-user-for-an-address`, `ask-a-user-for-a-birthday` (often required for personal credentials), `expand-or-collapse-part-of-a-form` (for fitness questions or terms acceptance).

**Gaps:**
1. No declaration/attestation pattern. Most licences require the citizen to declare facts under penalty (no criminal record, fit for work, etc.) — no example shows this.
2. No fitness-or-qualifications composer. Permits often require proof of training, experience hours, or supervisor sign-off.
3. No fee-with-application pattern. Many licences require payment at submission; no example couples form completion with a payment step.
4. No outcome-with-credential view. The `result-page` exists but there's no example of "here's your decision and your printable/wallet credential."
5. No renewal-from-existing pattern. Renewing should pre-fill from the existing record; no example captures this read-modify-confirm shape (this overlaps with `renew-something` type).

**Proposed new examples:**
- **Attestation/declaration.** Section pattern with explicit affirmation, plain-language consequences, signature/check.
- **Qualifications composer.** Section for showing training, hours, or external evidence.
- **Pay-and-submit.** Coupled flow joining form review → payment → submission.
- **Issued credential page.** Page-scale pattern showing the decision and the credential (with print, save, or wallet-add affordances).

---

## 4. `register-something`

**ProductTypes used:** `public-form` for many; some are pure transactional (no public-form needed, just confirmation).
**Existing examples (page-scale):** `public-form/start-page`, `public-form/question-page`, `public-form/result-page`. Birth/vehicle/marriage registrations don't really fit the question-page metaphor though — they're shorter and more form-like.
**Existing examples (interaction-scale):** `ask-a-user-for-a-birthday`, `ask-a-user-for-an-address`, `select-one-or-more-from-a-list-of-options`.

**Gaps:**
1. No short-form registration pattern. Public-form is page-per-idea (one question per page) which is overkill for "register a birth" or "register a vehicle." Need a denser, multi-fields-per-page pattern.
2. No registry-confirmation receipt pattern. Result-page is decision-shaped (approved/denied); registrations should show the registry entry that was created with a record ID.
3. No update-existing-registration pattern. Registries are alive — change of address, name change after marriage. No template captures the "look up existing → modify → resubmit" shape.

**Proposed new examples:**
- **Compact form page.** Multi-field registration form (12-20 fields) on one or two pages, denser than the public-form per-idea pattern.
- **Registry receipt.** Page showing the created record with ID, key facts, downloadable PDF, follow-on actions.
- **Update an existing record.** Look-up → modify → confirm → updated-record-receipt flow.

---

## 5. `pay-a-fee-or-fine`

**ProductTypes used:** Neither productType cleanly fits; this is a single-page transaction shape with no exploration. **Candidate for a new productType: `transaction` or `payment`.**
**Existing examples (page-scale):** None directly. `basic-page-layout` for the surrounding chrome.
**Existing examples (interaction-scale):** `copy-to-clipboard` (for receipt numbers).

**Gaps:**
1. No payment page pattern. There's no example showing amount-due, payment method selector, payee/payor, terms, submit-and-receipt.
2. No dispute path pattern. Many fines have a "pay or dispute" choice on the same surface; no example captures the branching.
3. No receipt page pattern. After paying, the citizen needs proof; no example.
4. No look-up-then-pay pattern. Many fines require finding your fine first (by ticket number, licence plate); no example couples lookup with payment.

**Proposed new examples (likely earns its own productType in a future PR):**
- **Lookup-and-pay.** Two-step flow: find the obligation, then pay it.
- **Pay-or-dispute.** Page that presents the amount and a clear branch to dispute.
- **Payment receipt.** Confirmation page with downloadable proof.
- **Account-balance view.** For multi-payment obligations (royalties, taxes), a balance-and-history page.

---

## 6. `renew-something`

**ProductTypes used:** `public-form` (light-weight version) but most existing examples assume new applications, not renewals.
**Existing examples (page-scale):** `public-form/start-page`, `public-form/review-page` (good for confirming pre-filled info), `result-page`.
**Existing examples (interaction-scale):** `disabled-button-with-a-required-field` (relevant when renewal can't proceed without a missing field), `confirm-a-change`.

**Gaps:**
1. No look-up-existing pattern. Renewal starts with verifying who you are and pulling up your existing record — no example captures the authentication-and-look-up step.
2. No diff-from-current pattern. Renewal usually shows "here's what we have on file; change anything?" — no example.
3. No renewal-reminder/notification pattern. Many renewals are time-bound; the system should notify in advance. No notification example covers this.
4. No combined-fee-and-credential issuance.

**Proposed new examples:**
- **Verify-and-renew.** Authenticate → see current record → confirm or edit → pay → updated credential.
- **Renewal reminder.** Email/notification template + landing page for the renewal start.
- **Updated credential receipt.** Same as #3's "issued credential page" but explicit on it being a renewal.

---

## 7. `check-status-or-records`

**ProductTypes used:** Could be a new productType — `account` or `portal`. Currently the existing examples are scattered.
**Existing examples (page-scale):** None directly. `basic-page-layout` for chrome.
**Existing examples (interaction-scale):** `display-user-information`, `show-status-on-a-card`, `show-quick-links`, `show-a-user-progress`, `show-a-user-progress-when-the-time-is-unknown`, `set-a-specific-tab-to-be-active`, `show-version-number`, `show-multiple-tags-together`, `show-full-date-in-a-tooltip`.

**Gaps:**
1. No authenticated-account-home pattern. Citizens checking their student loan or health coverage land somewhere — no example captures that landing page.
2. No history/timeline pattern. "Show me my claim history" or "show me my support payments" needs a timeline-shaped view; no example.
3. No status-with-action-affordance pattern. Often the status check leads to action (apply for a deferral, dispute a charge); no example handles "look up → see → act."
4. No record-detail pattern. After clicking a row in a history, the citizen sees the detail of that one record.

**Proposed new examples (probably needs its own `account` productType):**
- **My-account home.** Landing page with status cards, recent activity, and quick actions.
- **History timeline.** List of past events (payments, decisions, applications) with filters and detail-view links.
- **Record detail with actions.** Page showing one record's full info with contextual actions (renew, dispute, download).

---

## 8. `report-a-concern-or-incident`

**ProductTypes used:** `public-form` (lightweight version — no eligibility, no decision, just submission).
**Existing examples (page-scale):** `public-form/start-page`, `public-form/question-page` (the question variants), `result-page` (re-purposed for "report received" rather than "decision").
**Existing examples (interaction-scale):** `ask-a-user-for-an-address` (location of incident), `ask-a-user-for-a-birthday` (often DOB of subject), `add-another-item-in-a-modal` (multiple incidents or witnesses).

**Gaps:**
1. No anonymous-reporting affordance. Many reports allow or require anonymity (child abuse, fraud); no example covers the "do you want to provide your name" branch.
2. No report-receipt-with-reference-number pattern. Reporters need a way to follow up; no example captures the post-report receipt.
3. No file-evidence-with-context pattern. Photos, documents need to be tied to specific facts in the report; no example captures this.
4. No urgency-routing pattern. Some reports are time-critical (animal disease outbreak, wildfire); no example shows how to flag urgency in the form.

**Proposed new examples:**
- **Optional-identity report form.** Pattern showing the anonymous/named branch clearly with consequence framing ("if anonymous, we can't follow up with you").
- **Report receipt.** Page showing reference number, what happens next, contact path if more info.
- **Evidence-attached-to-fact.** Section pattern for uploading evidence linked to specific report items.

---

## 9. `file-a-complaint`

**ProductTypes used:** `public-form` (slightly heavier than report — usually requires identity).
**Existing examples (page-scale):** `public-form/*` family, `review-page`, `result-page`.
**Existing examples (interaction-scale):** `ask-a-user-for-an-address`, `ask-a-user-for-a-birthday`, `ask-a-long-answer-question-with-a-maximum-word-count` (useful for the narrative of a complaint), `give-more-information-before-asking-a-question-a` and `-b`.

**Gaps:**
1. No "describe what happened" pattern with timeline support. Complaints often need a sequence of events; no example handles ordered narrative input.
2. No regulator-context pattern. The citizen is filing against a regulated party — they need to find/identify that party. No example captures "search for the regulated entity, link to it, then file."
3. No status-update notification pattern. Investigations take months; no example covers the "your complaint is in stage X" comms.
4. No outcome-letter pattern. After investigation, the citizen gets a decision letter — `result-page` is too thin for the complexity of complaint outcomes.
5. No appeal-pathway pattern (overlaps with the `appeal-a-decision` extension).

**Proposed new examples:**
- **Identify the regulated party.** Search-and-select pattern for finding the doctor/business/officer the complaint is about.
- **Timeline-of-events.** Section pattern for ordered narrative input.
- **Investigation status updates.** Pattern for the in-progress status page (this overlaps with `check-status-or-records`).
- **Decision letter view.** Long-form decision page with reasoning, next steps, and appeal info.

---

## 10. `find-a-service-or-place`

**ProductTypes used:** Could be a new `directory` productType. Today the closest is the `search` example (singleton).
**Existing examples (page-scale):** `search` (current example, single).
**Existing examples (interaction-scale):** `card-grid`, `header-with-navigation`, `hero-banner-with-actions`, `show-a-list-to-help-answer-a-question`, `show-multiple-tags-together`, `show-quick-links`, `link-to-an-external-page`.

**Gaps:**
1. No location-based-search pattern. Finding a doctor "near me" is a common pattern — no example handles geolocation or postal code input with results map.
2. No filter-by-criteria pattern for a directory. The existing `filter-data-in-a-table` is for tabular admin data, not citizen-facing directory.
3. No directory-card-with-contact-info pattern. Each result needs hours, contact, accessibility, eligibility hint — no example captures the standard result card for a public-facing directory.
4. No no-results-with-recovery pattern. When nothing matches, what do citizens see? No example handles the empty state with helpful recovery.

**Proposed new examples (likely earns a `directory` productType in future):**
- **Directory search page.** Combined filters + results in a public-facing directory shape.
- **Provider/place card.** Standard result card with the right facts: name, location, hours, contact, eligibility, accessibility.
- **Empty state with recovery.** No-results pattern that suggests broader searches or contact.
- **Result detail page.** Click-through view of one provider with full info.

---

## 11. `search-a-public-register`

**ProductTypes used:** Same `directory` productType candidate as above, but the user intent is verification rather than provider-selection.
**Existing examples (page-scale):** `search` (singleton, again).
**Existing examples (interaction-scale):** Same as 10, plus `display-user-information`, `show-status-in-a-table` (for paid registry results).

**Gaps:**
1. No verify-a-fact pattern. "Is this professional registered?" is yes/no with details — no example handles the binary verification result with supporting record.
2. No paid-search-with-payment pattern. Court records and land titles cost money; no example couples lookup → payment → record retrieval.
3. No record-citation pattern. After finding a record, the citizen often needs to cite it (legal proceedings, applications). No example shows how to make a record citable/printable.

**Proposed new examples:**
- **Verification result.** "We found one match; here's what they're authorized to do" — yes/no with detail.
- **Paid-record retrieval.** Three-step pattern: search → confirm + pay → retrieve.
- **Citation-ready record view.** Printable, downloadable, or share-link pattern.

---

## 12. `read-information-or-guidance`

**ProductTypes used:** Out of scope for productTypes — this is content/IA territory more than action design.
**Existing examples (page-scale):** `basic-page-layout` (the only one that fits), `hero-banner-with-actions`.
**Existing examples (interaction-scale):** `show-links-to-navigation-items`, `show-quick-links`, `link-to-an-external-page`, `hide-and-show-many-sections-of-information`, `show-a-section-title-on-a-question-page` (re-purposable as content section).

**Gaps:**
1. No structured-guidance page pattern. Long-form content with intro, sections, summaries needs canonical examples.
2. No "rules and rights" pattern. Content explaining citizen rights or business obligations is common across ministries; no example.
3. No content-with-tools pattern. Some guidance has interactive tools embedded (calculators, eligibility checkers). No example.

**Proposed new examples (low priority — this is the lowest-action service type):**
- **Long-form guidance page.** Standard structure for explanatory content.
- **Rules-and-rights page.** Specific pattern for rights/obligations content.
- **Inline calculator.** Mini-tool embedded in guidance.

**Note:** This service type is the largest in the corpus (80 services) but has the lowest design-system value because it's content rather than action. Brief 07 should surface it as "this category exists; the design system does not yet differentiate offerings here." The honest gap is "the design system today is action-shaped; this category would need a new content-shape that doesn't exist."

---

## 13. `access-an-in-person-program`

**ProductTypes used:** None today (no digital surface). The relevant pattern is `find-a-service-or-place` pointing at the program.
**Existing examples (page-scale):** None — these services have no digital citizen surface.
**Existing examples (interaction-scale):** None directly applicable.

**Gaps:**
1. By definition this is the gap. ~11% of Alberta services have no digital channel.

**Proposed:**
- **No new examples in this brief.** Brief 07 should surface this category as "services without a digital surface; design system can't help build for these until digitization decision is made." The forward-looking response is intake-and-assess productType pairs (worker side), pursued in a follow-up brief per scope.

---

## 14. `appeal-a-decision` (Kate Tarling extension)

**ProductTypes used:** `public-form` (light) for the citizen submission; workspace for the reviewer side (worker, deferred).
**Existing examples (page-scale):** `public-form/*`.
**Existing examples (interaction-scale):** `ask-a-long-answer-question-with-a-maximum-word-count` (grounds for appeal), `expand-or-collapse-part-of-a-form`.

**Gaps:**
1. No reference-the-original-decision pattern. Appeals start with a specific prior decision — no example handles linking to it or summarising it.
2. No grounds-for-appeal composer. Appeals require structured reasons (procedural error, new evidence, etc.).
3. No appeal-status-tracking. Same as #1's status tracker but for appeals specifically.
4. No appeal-outcome-with-action pattern. Outcomes can be uphold/overturn/remit; the affordances each implies differ.

**Proposed new examples:**
- **Appeal initiation.** Page that loads the original decision, lets the appellant select grounds, write reasoning.
- **Appeal status.** Status tracker variant for appeals.
- **Appeal outcome.** Decision letter pattern with the three possible branches (uphold, overturn, remit).

---

## Cross-cutting gaps (apply to multiple service types)

These gaps surface across the analysis. Naming them once so they're not repeated in the artifact:

1. **Eligibility checking** — needed before `apply-for-a-benefit`, `apply-for-a-licence-or-permit`, `apply-for-a-grant-or-funding`. No canonical pattern.
2. **Status tracking after submission** — needed after every Apply-shape and Report-shape and Complaint. The current `result-page` only covers the immediate confirmation, not the long wait.
3. **Save-and-return across sessions** — long applications can't be done in one sitting.
4. **Authentication / account home / portal** — `check-status-or-records` needs this; many other types benefit from it. There's no `account` or `portal` productType.
5. **Payment as a step** — couples with renewals, licence applications, paid registry searches, fees and fines. No `payment` productType.
6. **Notifications and follow-up** — every Apply-shape generates notifications (received, status changed, decision issued, renewal reminder). No notification example covers this depth.
7. **Decision letters** — outcome of Apply, Complaint, Appeal. Currently `result-page` is the only candidate and it's thin.

These cross-cutting gaps argue for new productTypes beyond `workspace` and `public-form` — at least `account`/`portal`, `payment`/`transaction`, and possibly `directory`. Phase 4 will surface this as a finding in the artifact, even though productType decisions live with PR-3888-style work, not Brief 06.

---

## Phase 4 hand-off

The structured artifact at `goa-service-maps/data/ab/service_types.json` will carry, per service type:

- `id`, `name`
- `service_task`, `kate_tarling_intents[]`
- `leverage` (mechanically verified)
- `services[]` (named members from the data)
- `shared_shape`, `variations`
- `product_types_used[]`
- `existing_examples[]` (referencing slugs from this doc)
- `gaps[]` (per-type gaps from this doc)
- `proposed_examples[]` (per-type proposals from this doc)

Plus top-level fields:
- `cross_cutting_gaps[]` (the seven cross-cutting items above)
- `excluded` (Engage, in-person-only category, scheduling-as-candidate-15, buying-as-EM-only)
- `kate_tarling_intents[]` (canonical list with IDs)
- `service_tasks[]` (canonical list including Find/Advise extensions)
