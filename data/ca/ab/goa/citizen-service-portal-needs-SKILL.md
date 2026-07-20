---
name: citizen-service-portal-needs
description: Scope and draft user needs for a citizen-facing portal over a specific government service. Use whenever the user wants to design or plan a digital portal for a government program (e.g. AISH, Income Support, PDD, child care subsidy, seniors benefits) — producing a journey-staged user-needs document, priority-grouped companion view, MVP scoping doc, information-architecture navigation map, recipient lifecycle diagram, boulders/rocks/pebbles scope breakdown, and prototype wireframes using the relevant production design system. Best when service map data (e.g. from goa-service-maps) and a policy reference are available.
---

# Citizen Service Portal Needs

You are helping a product, service, or design lead scope a citizen-facing portal for a specific government service. The output is a tightly evidence-grounded working draft document plus a small family of companion artifacts that together define what users need from the portal, prioritized, ready for design build planning.

## When this skill applies

- The user wants to "draft a plan", "scope", "design", "build out user needs", or "plan a portal" for a specific citizen-facing government program.
- The work centers on improving citizen experience around status, transparency, self-service, accountability, or operational pain.
- The user has — or can connect — relevant source material: a service map, a policy manual, public-discourse evidence, design system access.

## Phase 1 — Clarify intent before starting

Always ask before producing any deliverable. Defaults that are wrong here waste hours.

Ask about:

1. **Source material.** Service map data location? Policy manual reference? Existing user research?
2. **Audience.** Internal product/service team? Executive/ministry leadership? Just the user? Layered?
3. **Format.** Markdown working doc? HTML? Both? Other?
4. **Depth.** Broad inventory? Top-10 deeply prioritized? Journey-staged?
5. **Scope boundaries.** Which program/ministry/jurisdiction specifically? Which user populations (recipients only, or applicants, helpers, advocates)?

Also: **challenge the brief**. Surface and name your assumptions before doing work. Especially around abstract framings like "transparency", "accountability", or "engagement" — what do they mean *from a citizen perspective specifically*?

## Phase 2 — Research and ingestion

Gather evidence in this order:

1. **Service map data** (local JSON if available — see the service-map-data skill for structure). Extract the ministry, program, supporting services, channels, and legislation references.
2. **Policy manual** — read the key chapters in priority order: eligibility/application, ongoing obligations, benefits, overpayments, appeals, third-party authorization. Identify specific obligations, rights, decision points, dollar amounts, timing rules.
3. **Public discourse** — news, advocacy organizations (e.g. Inclusion Alberta, VAD), Ombudsman case summaries, op-eds. **Be explicit about selection bias** — people who post are disproportionately in crisis, organized through advocacy, or denied. Read as a map of visible pain, not a map of experience.
4. **Benchmarks** — comparable portals: SSA's *my Social Security*, UK GOV.UK PIP, Code for America Integrated Benefits work. Use as directional reference, not templates — populations and politics differ.

Throughout: maintain a clear separation of evidence sources. The doc uses pills: **SM** (service map), **P** (policy), **B** (benchmark), **D** (discourse), plus inline notes for tech architecture, program knowledge, equity principle. Add tooltips on every chip so readers don't have to scroll back to a legend.

## Phase 3 — Draft the journey-staged user needs document

Produce as a single HTML file (matches the rest of the deliverable family). Structure, in order:

1. **Title + version eyebrow** at top.
2. **Problem statement** — above the table of contents. Tight, citizen-centred, single paragraph. ("After an Albertan applies for AISH, the experience of staying in the program is opaque and fragmented…")
3. **Table of contents.**
4. **§1 Framing &amp; assumptions** — scope statement, primary user population, explicit out-of-scope, assumptions list. Push back on the brief here where warranted.
5. **§2 Source material** — what evidence is used and the pill legend.
6. **§3 How needs are prioritized** — P0/P1/P2 definitions. Be precise: P0 = the portal is not credible without this. P1 = core, ship in v1. P2 = important but defer-able. Optional P3 = later phase.
7. **§4 Journey-staged user needs** — one section per lifecycle stage. Mark out-of-scope stages visibly (dimmed/dashed) and explain why they're out. Each stage has:
   - Numbered title (e.g. "Stage 3: Wait for & track the assessment process")
   - One-line blurb
   - Optional callout that surfaces a key insight ("What this stage is really about: …")
   - Needs table: user need, why it matters, priority, evidence
   - For complex stages, sub-tables (e.g. approved path / denial path)
8. **§5 What the policy manual adds** — manual-derived needs, with corrections to earlier figures.
9. **§6 Public discourse review** — visible pain points with bias caveats explicitly stated, themes by signal strength.
10. **§7 Cross-cutting needs** — split into three groups: **design qualities** (constraints — accessibility, mobile-first, tone &amp; dignity, error tolerance, multilingual, offline parity, trust signals), **infrastructure** (foundation work — delegated authority shared service, notifications infrastructure, persistent record), **features** (actual portal capabilities — third-party access, decision explainability, federal-benefit awareness, notification preferences, secure messaging). This grouping matters because it tells the reader what is a buildable feature vs what is a constraint that applies to everything.
11. **§8 Prioritized top-10** — across all stages and cross-cutting. Note items that were reordered and why.
12. **§9 Out of scope &amp; open questions** — scope framing, explicit deferrals, open questions to resolve early.
13. **§10 Assumptions, uncertainties &amp; what couldn't be verified** — honesty section. Surface every assumption and every claim that needs validation. Also: challenges to the original brief.
14. **Version history** — at the bottom, not the top.

## Phase 4 — Iterate with the user

Walk through each section in dialogue. Make changes after each turn. Common refinements:

- **Stages 1–2 (discovery, application) are often out of scope** — they're usually existing infrastructure with other tracks. Mark visibly but keep for context.
- **Reframe stage names** from citizen perspective ("Wait & track the assessment process" not "Adjudication window").
- **Watch for internal-language leakage** — "adjudication", "case under review", "client" — citizens don't talk this way.
- **Watch for replacement framing** — should be augmentation. Letters, phone, in-person remain.
- **Watch for assumed integrations** that aren't realistic — e.g. real federal-government data integration is rarely feasible.
- **Consolidate overlapping needs** — appeals overlap with decision-explainability and Stage 4 denial path; payment history overlaps with proof-of-enrollment because the remittance statement often serves both purposes.
- **Flag program-integrity considerations** on transactional features (e.g. impact preview reframed as post-submission explanation rather than pre-submission preview, to avoid enabling gaming).
- **Use "ephemeral" markers** for stages that are time-bounded (e.g. a transition cohort that closes on a specific date).

## Phase 5 — Produce companion artifacts

After the main draft is stable, generate companion HTML files (one per artifact):

1. **Priority-grouped view** — auto-generated from the main draft (parse needs by priority). P0 / P1 / P2 in colour-coded tables with stage tag inline.
2. **MVP scoping doc** — delivery model, stack, design scope vs MVP wiring scope, what's in MVP, what's deferred to phase 2, dependencies and risks, open questions.
3. **Navigation map (IA)** — card-based sitemap grouped by user relationship to the section (e.g. day-to-day / process-driven / always-available / settings). **Avoid auto-laid-out Mermaid for IA** — it gets unreadable fast. HTML grid cards are clearer.
4. **Recipient lifecycle diagram** — Mermaid flowchart showing the sequence (Wait → Decision → Commencement → Receiving) with conditional branches (Re-apply, Appeals, Exit). Use solid arrows for the primary path, dashed for conditional or recurring. Limit to 2 colour ramps; include a legend.
5. **Scope breakdown — boulders, rocks, pebbles** — user-perspective sizing of the scope. Boulders = the portal isn't credible without these (typically 4–6 items). Rocks = significant features that broaden value (typically 8–12). Pebbles = refinements and polish (typically 10–15). Constraints (design qualities) are separate and don't sequence.
6. **Prototype wireframe** — at least one key screen (usually the Home/Dashboard) using the production design system. For the GoA stack, that's `@abgov/web-components` loaded from unpkg with `ionicons` for icons. Use real component tags (`goa-app-header`, `goa-callout`, `goa-card`, `goa-button`, `goa-icon`) — not "inspired styling". Reference design.alberta.ca for correct attribute names and slot patterns. Verify the brand fonts will load in the deployed context (Adobe Typekit is domain-restricted — local `file://` previews will fall back to system fonts; acknowledge this rather than chasing it).

## Key principles to apply throughout

- **Augmentation, not replacement.** The portal sits alongside existing channels (letters, phone, in-person), never replaces them. Every need's rationale should reflect this.
- **Coherent vertical slices for MVP.** If a stage is in MVP, *all* its needs ship end-to-end. "Show next payment but not history" creates the disjointed experience that breaks user trust.
- **Design covers everything in scope; MVP is a wiring choice.** Phase 2 needs still get designed — they ship as completed surfaces awaiting back-end wiring. Cost of designing now is small; cost of designing later is much larger.
- **The helper layer is first-class.** Trustees, financial administrators, attorneys under POA, family, advocates are not a niche use case. Delegated authority is a shared-service architectural concern, not a portal-only feature.
- **Distinguish design qualities from infrastructure from features.** Don't conflate. Accessibility is a constraint. Notifications infrastructure is foundation. Notification preferences is a feature.
- **Program-integrity considerations on transactional features.** Anywhere the portal lets a recipient submit information, ask: does showing impact before submission enable gaming? Default to post-submission explanation.
- **Honesty about evidence.** Every claim is tagged by source. Unverified claims are explicit. Things that "could not be verified" are surfaced.
- **Strong opinions loosely held.** Commit to positions with rationale; accept pushback gracefully. Document version-by-version what changed and why.

## Tone and posture

- **Challenge user assumptions when warranted.** Especially abstract framings like "transparency", "accountability", "engagement". What do they mean *for the citizen*?
- **Cite source.** Every figure, every claim, every benchmark — sourced or explicitly inferred.
- **Surface hallucination risk.** Every doc has an explicit "assumptions and what I couldn't verify" section.
- **Use precise language.** "Recipients in financial difficulty" not "needy people". "Plain-language decisions" not "user-friendly notices".
- **Avoid pretending technical decisions are user decisions.** Tech availability informs sequencing but doesn't define MVP.

## Tools and references

- **Service-map-data skill** — for service map JSON structure.
- **GoA Design System** (`@abgov/web-components`, design.alberta.ca, ui-components.alberta.ca, github.com/GovAlta/ui-components).
- **GoA Public form pattern** — the right pattern for citizen-facing applications (vs the Workspace pattern for staff).
- **Mermaid** — for lifecycle diagrams. Avoid for IA (too dense).
- **HTML for all deliverables** — consistent styling across the doc family.

## Output structure

The complete deliverable family for one program is typically 5–6 HTML files, all in one directory:

- `{program}-portal-user-needs.html` — the main working draft (versioned, e.g. v0.16)
- `{program}-portal-user-needs-by-priority.html` — auto-generated priority view
- `{program}-portal-mvp-scoping.html` — MVP scope statement
- `{program}-portal-mvp-navigation-map.html` — information architecture
- `{program}-portal-mvp-recipient-lifecycle.html` — journey diagram
- `{program}-portal-scope-breakdown.html` — boulders/rocks/pebbles
- `{program}-portal-wireframe-{screen}.html` — at least one prototype screen

All files cross-reference each other in the footer. The main working draft is the canonical source; the others derive from it and can be regenerated as the main draft evolves.

## What this skill is NOT for

- A scope or PRD for an existing portal undergoing iteration (use a more conventional product spec).
- Internal/staff-facing tools (use the Workspace pattern, not the Public form pattern).
- A pure UX research report (this skill produces design-build-ready scope, not just findings).
- Cross-program portal strategy (one program at a time).
