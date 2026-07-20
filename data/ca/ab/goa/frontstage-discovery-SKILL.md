---
name: frontstage-discovery
description: First phase of Service Design Discovery (SDD) for the frontstage (citizen-visible) layer of a government service. Use whenever a user wants to scope a citizen-facing portal or digital surface for a specific government program (e.g. AISH, Income Support, PDD, child care subsidy, seniors benefits) — producing a tight four-artifact deliverable family (journey-staged needs draft, priority-grouped view, MVP scoping doc, boulders/rocks/pebbles scope breakdown) that feeds the conceptual modeling, user flow, and prototyping phases that follow. Sibling skill `backstage-discovery` handles staff-facing surfaces of the same service. The two skills are independent — neither requires the other layer to also be in scope. Do not use for downstream phases (conceptual modeling, user flow modeling, prototyping) — those are separate skills or human-led work.
---

# Frontstage Discovery

This skill performs **phase 1** of Service Design Discovery (SDD) for the **frontstage** layer of a government service — the citizen-visible portion, including interactions performed by delegated representatives (where the program has that need).

The output is a tight, evidence-grounded deliverable family that captures, prioritizes, and scopes what frontstage actors need — ready to feed the downstream phases of SDD.

## The methodology this skill is part of

Service Design Discovery (SDD) is an accelerated approach to scoping digital services. It preserves service-design thinking as its intellectual foundation but replaces the traditional pipeline (deep discovery → iterative build-test-learn → 6+-month agile development) with a faster, phased sequence:

| # | Phase | Mode | Audience |
|---|---|---|---|
| **1** | **Discovery** *(this skill, plus sibling `backstage-discovery`)* | Skill-driven synthesis | Team reviews |
| 2 | Interim conceptual modeling | Team workshop | Capability map (presentation), ecosystem &amp; domain diagrams (workshop) |
| 3 | User flow modeling | Team-produced | Navigation/IA + lifecycle/journey flows |
| 4 | Collaborative validation with users | Two-way | Actual users |
| 5 | Production-stack prototyping | Build in real tech | HTML on the production component library |
| 6 | Rapid iteration with users on the stack | User testing on live code | Actual users |

**This skill produces only phase 1 artifacts.** Other phases are handled by sibling skills (some still in development) or by human-led work. The orchestrator across phases is human-led for now.

## When this skill applies

- The user wants to scope a citizen-facing portal or digital surface for a specific government program.
- The work centers on improving the experience of recipients, applicants, or (where applicable) their delegated representatives.
- The user has — or can connect — relevant source material: legislation, policy manual, service map data, public discourse, benchmarks.

This skill is for the **frontstage** layer only. For staff-facing tools that produce frontstage outcomes (assessment, adjudication, case management, intake processing), use the sibling `backstage-discovery` skill.

## Frontstage and backstage can be modernized independently

This is foundational. Frontstage and backstage are **not coupled in delivery or in discovery**. Either can be improved without the other moving. The skill must respect this.

In practice:
- A modern frontstage can ship to a legacy backstage (e.g., the portal generates a PDF that drops into a paper-based backend). This is common in government — partial modernization is the rule, not the exception.
- A modern backstage can be fed by paper applications, email submissions, in-person intake. The backstage modernization doesn't require the frontstage to also move.
- The leveraged improvement often lives on one side only. Discovery should surface this honestly.

The **interface between layers** matters and should be surfaced explicitly: how does data pass from frontstage to backstage today, and what's the proposed form (PDF? structured API? somewhere in between?). The MVP scoping doc should make the interface assumption explicit so the team can decide whether to constrain the frontstage MVP to the current backstage's capabilities or push for both layers to move together.

## What this skill produces

Four HTML artifacts, all in one directory, all cross-referenced in their footers, all version-stamped (e.g. v0.16) and labelled "Service Design Discovery · Phase 1":

1. **Journey-staged needs draft** *(the canonical working document)*
   - Problem statement (above the TOC)
   - Framing &amp; assumptions (scope, primary user population, explicit out-of-scope, assumed state of the other layer)
   - Source material (with the evidence pill legend)
   - Prioritization criteria (P0/P1/P2 with sharp definitions)
   - Journey stages, one per lifecycle position. Each has a one-line blurb plus a needs table (user need, why it matters, priority, evidence). Out-of-scope stages are kept visible but dimmed.
   - Cross-cutting needs, split into three groups: **design qualities** (constraints), **infrastructure** (foundation), **features** (capabilities).
   - Top-N prioritized list across all stages and cross-cutting.
   - Out of scope &amp; open questions.
   - Assumptions, uncertainties &amp; what couldn't be verified.
   - Version history (at the bottom).

2. **Priority-grouped companion view** — auto-generated from the needs draft. Needs flipped to P0 / P1 / P2 tables with stage tag inline. For scoping conversations and effort sizing.

3. **MVP scoping doc** — delivery model, what's in MVP vs phase 2, dependencies, risks, the proposed frontstage-backstage interface, open questions to resolve early.

4. **Scope breakdown — boulders, rocks, pebbles** — user-perspective sizing. Boulders = fundamental to credibility (typically 4–6). Rocks = significant features (typically 8–12). Pebbles = refinements (typically 10–15). Constraints (design qualities) are separate and don't sequence.

## What this skill explicitly does NOT produce

The discipline of the methodology depends on respecting phase boundaries.

- **Capability map, ecosystem diagram, domain model** — these are **phase 2** (interim conceptual modeling) artifacts. The needs draft produces *inputs* to phase 2 but does not pre-empt the team-internal alignment work.
- **Navigation map / information architecture, lifecycle / journey diagrams** — these are **phase 3** (user flow modeling) artifacts.
- **HTML wireframes or prototypes** — **phase 5** (production-stack prototyping) work. Skipping phases 2 and 3 to jump straight to wireframes produces shallow output that lacks model alignment.

When prior versions of this skill produced these downstream artifacts inside phase 1, the results were reasonable-looking but lacked the rigour that the methodology's middle phases produce. The skill is deliberately scoped to its phase.

## Phase 1 process — five steps

### Step 1: Clarify intent and surface program characteristics

**General clarifying questions:**

1. **Source material** — legislation reference? policy manual reference? service map data? existing user research?
2. **Audience** — internal team? executive/leadership? both?
3. **Format** — HTML is the SDD default; only ask if uncertain.
4. **Depth** — broad inventory? journey-staged? top-N deeply prioritized?
5. **Scope boundaries** — which program / ministry / jurisdiction? which frontstage actor populations?
6. **Whose work is this, and who experiences the outcome?** If the same person, this is frontstage. If different, double-check the request isn't actually for backstage.
7. **State of the other layer** — what's the backstage that this frontstage will connect to? Modernization in progress, legacy, paper-based, hybrid? The answer shapes what frontstage scope is realistic and where the interface lives.

**Program characteristics to surface during clarification or early research:**

These are *findings* that materially shape the discovery — not principles to assume up front. The skill should investigate, not assert.

1. **Channel posture.** Can this program go digital-only, or must existing channels (letters, phone, in-person) remain available because of recipient population characteristics or backstage limitations? Don't assume augmentation; ask whether augmentation is required.
2. **Helper / proxy access.** Does the recipient population include people who can't independently interact digitally — by cognitive ability, language, accessibility, or other constraint? If so, how robust does helper/proxy access need to be — a full delegated-authority shared service, or simpler share/view patterns?
3. **External-program entanglements.** Are there federal, municipal, or other-ministry programs that the recipient must navigate in concert? If so, how visible should those touchpoints be?
4. **Recipient capacity assumptions.** What can we assume about the recipient population's digital literacy, connectivity, language, cognitive load tolerance? This calibrates accessibility intensity, multilingual scope, plain-language register.
5. **Evidence-source richness.** Some programs have rich public discourse (AISH, Income Support); niche programs may have little. Be honest about evidence weight rather than pretending equal richness across sources.

**Challenge the brief.** Surface and name assumptions before doing work. Especially abstract framings ("transparency", "accountability", "engagement") — what do they mean *from the frontstage actor's perspective specifically*?

### Step 2: Research and ingestion

Gather evidence in this order. Maintain clear source separation throughout.

1. **Legislation.** Start with what is *legally required* — the immutable grounding. Service map data may include legislation cross-references; use those. Identify the statutory obligations, rights, and decision points.
2. **Policy manual.** How the legislation is implemented in practice. Distinguish between policy that's required by legislation and policy that's discretionary. **Policy has flexibility in the right circumstances.** If discovery surfaces a serious frontstage need that conflicts with current policy, flag it for human consideration rather than assuming policy is fixed.
3. **Service map data** (local JSON if available — see `service-map-data` skill for structure). Extract ministry, program, supporting services, channels.
4. **Public discourse** — news, advocacy organizations, Ombudsman case summaries, op-eds. **Be explicit about selection bias** — read as a map of visible pain, not of experience. Note when public discourse is rich vs. thin.
5. **Benchmarks** — comparable portals (e.g. SSA, GOV.UK PIP, Code for America). Directional reference, not templates — populations and politics differ.

Use evidence pills throughout: **L** (legislation), **P** (policy), **SM** (service map), **B** (benchmark), **D** (discourse), plus inline notes for tech architecture / program knowledge / equity principle. Add tooltips on every chip so readers don't have to scroll back to a legend.

### Step 3: Draft the needs document

Structure detailed in "What this skill produces" above. Notes:
- Problem statement comes **above** the TOC.
- Each stage has a one-line blurb plus needs table.
- Cross-cutting needs explicitly split into design qualities / infrastructure / features. Do not conflate these.
- Top-N prioritized list across stages and cross-cutting.
- Honesty section at the end: every claim that's unverified or inferred is named.
- Version history at the **bottom**, not the top.

### Step 4: Iterate with the user

Walk through each section in dialogue. Make changes after each turn. Common refinements:

- **Stages 1–2** (discovery, application) often out of scope — they're usually existing infrastructure with other tracks. Mark visibly (dimmed/dashed) but keep for journey context.
- **Reframe stage names** from the frontstage actor's perspective. Avoid internal-language leakage (e.g. "adjudication", "case under review", "client").
- **Watch for misframings** — e.g. if "augmentation" was assumed but the program could actually go digital-only, that surfaces as a question for the team.
- **Watch for assumed integrations** that aren't realistic (e.g. real federal-government data integration is rarely feasible).
- **Consolidate overlapping needs.**
- **Flag program-integrity considerations** on transactional features (e.g. impact preview reframed as post-submission explanation rather than pre-submission preview).
- **Use "ephemeral" markers** for time-bounded stages.

### Step 5: Produce the three companion artifacts

After the needs draft is stable, generate priority view, MVP scoping, and scope breakdown. All HTML, all cross-referenced in their footers.

## Cross-cutting needs — structure, not template

The cross-cutting cluster always has the same three-group structure:

- **Design qualities** — constraints that apply to how everything is built (accessibility, mobile-first, tone, error tolerance, multilingual support, offline parity).
- **Infrastructure** — foundation work consumed by multiple features (notifications plumbing, persistent record, identity, possibly delegated authority if the program needs it).
- **Features** — actual portal capabilities distinct from any single journey stage (decision explainability, secure messaging, notification preferences, third-party access UI, possibly federal-benefit awareness if relevant).

**What populates each group depends on what discovery surfaces.** The cross-cutting cluster from one program (e.g. AISH's delegated authority shared service, federal-benefit awareness, helper-layer load-bearing) is *that program's answer*, not the template. Other programs will have different cross-cutting clusters depending on their recipient population, channel posture, external-program entanglements, and capacity assumptions.

## Key principles to apply throughout

These are foundational to *how the skill works*, regardless of which program is being scoped.

- **Coherent vertical slices for MVP.** If a stage is in MVP, *all* its needs ship end-to-end. "Show next payment but not history" creates the disjointed experience that breaks user trust.
- **Design covers everything in scope; MVP is a wiring choice.** Phase 2 needs (in MVP-vs-phase-2 sense) still get designed downstream.
- **Distinguish design qualities from infrastructure from features** in the cross-cutting cluster.
- **Program-integrity considerations** on transactional features. Anywhere the portal lets a frontstage actor submit information, ask: does showing impact before submission enable gaming? Default to post-submission explanation.
- **Honesty about evidence.** Every claim tagged by source. Unverified claims explicit. Things that "could not be verified" surfaced openly.
- **Respect the legislation as immutable; treat policy as adjustable in the right circumstances.** Flag, don't assume.
- **Strong opinions loosely held.** Commit to positions with rationale; accept pushback gracefully. Document version-by-version what changed and why.

## Division of labour — skills synthesize, humans decide

This skill produces artifacts that the team reviews and refines. It does not make scope decisions, prioritization calls, or strategic trade-offs unilaterally. When the skill flags an open question or a needs-validation item, that's an explicit invitation for human judgement — not a placeholder to be auto-filled.

## Tone and posture

- **Challenge user assumptions** when warranted, especially abstract framings.
- **Cite source.** Every figure, every claim, every benchmark — sourced or explicitly inferred.
- **Surface hallucination risk.** Every doc has an explicit "assumptions and what I couldn't verify" section.
- **Use precise language.** "Recipients in financial difficulty" not "needy people". "Plain-language decisions" not "user-friendly notices".
- **Don't pretend technical decisions are user decisions.** Tech availability informs sequencing but doesn't define MVP.

## Tools and references

- **`service-map-data` skill** — for service map JSON structure.
- **GoA Design System** — for vocabulary and pattern references. Public form pattern is the relevant reference for frontstage work; `design.alberta.ca` is canonical.
- **Sibling skill `backstage-discovery`** — for the staff-facing layer of the same service. Independent of this skill; each can be invoked on its own.

## What this skill replaces

Within Service Design Discovery, this skill replaces the **discovery and scoping phase** that in traditional service design would produce a service blueprint as its primary artifact. The deliverable family carries the intent forward (multi-actor visibility, evidence-grounded synthesis, scoping decisions) in a form that drives directly into the subsequent SDD phases — without the documentation-centric handoff a blueprint typically becomes.

SDD as a methodology replaces the traditional 6+-month discovery-to-launch pipeline with a much faster sequence. This skill is the first node in that pipeline.

## File naming convention

For a program with short code `{program}` (e.g. `aish`, `dia`):

- `{program}-portal-user-needs.html` — the main working draft
- `{program}-portal-user-needs-by-priority.html` — priority-grouped view
- `{program}-portal-mvp-scoping.html` — MVP scoping doc
- `{program}-portal-scope-breakdown.html` — boulders/rocks/pebbles

All four in the same directory.

## What this skill is NOT for

- Scoping or refining an existing portal in iteration (use a conventional product spec).
- Backstage / internal / staff-facing tools — use the sibling `backstage-discovery` skill.
- Pure UX research reports (this skill produces scope, not just findings).
- Cross-program portal strategy (one program at a time).
- Conceptual modeling (capability map, ecosystem, domain) — **phase 2**.
- User flow modeling — **phase 3**.
- Production-stack prototyping or wireframes — **phase 5**.
- Anything past the first phase of SDD. Discipline of the methodology depends on respecting phase boundaries.

**Do not impose findings from one program onto another.** The skill discovers what *this* program needs; it does not assert what every program must have. "Augmentation, not replacement", "helper layer is first-class", "federal-benefit awareness as cross-cutting" are program-specific findings from AISH/ADAP — not universal truths. For each new program, run the discovery and let the evidence drive the cross-cutting cluster.

**Do not assume the other layer (backstage) is also being modernized.** The deliverables describe a complete frontstage scope that can ship to whatever backstage currently exists — modernized API, legacy paper-based intake, PDF-to-legacy-storage, or any hybrid. The MVP scoping doc names the interface assumption explicitly so the team can make that call deliberately.
