# Citizen Inquiry Patterns — Underserved Categories

*Reference material for an agent helping scope citizen-facing services in government programs. Derived from analysis of Alberta's AISH/ADAP program but the categories generalize to most government social assistance programs.*

## Purpose

Six categories of citizen inquiry that surface as **poorly served by traditional channels** (phone queues, mail, in-person visits). Use this when:

- Scoping a citizen portal or inquiry-handling product
- Evaluating where messaging / chat / conversational features fit in scope
- Identifying gaps in current channel coverage
- Triaging the kinds of questions a citizen-facing service needs to answer
- Pushing back on a "build an inbox" framing of secure messaging — the underserved space is bigger and more decomposable than one inbox

## The six categories

### 1. About-me — status and rationale

Recipients asking about their own file and history.

- "Where is my application?"
- "Why did my payment change?"
- "Why do I owe this money?"
- "Why was I denied?"

**Why current channels fail.** Phone agents can answer but the answer isn't searchable, savable, or shareable. Letters state outcomes without rationale ("your benefit is $X" without showing the formula). The data exists in case management but isn't exposed in any self-service surface.

**Best resolution.** Self-service data exposure in a portal — not a messaging product. Show status, show rationale, show what's been received.

### 2. Cross-system — questions that span bureaucratic boundaries

Federal/provincial, program-to-program, ministry-to-ministry.

- "Do I need to apply for the Canada Disability Benefit?"
- "Will Alberta claw back what I get federally?"
- "What's the difference between the federal $200 CDB and the provincial $200 transition benefit?"
- "How does this affect my CPP-D?"

**Why current channels fail.** Requires knowledge that crosses jurisdictional boundaries. No single channel is set up to span them. Provincial staff often aren't confident about federal program details, and vice versa.

**Best resolution.** Content explainers in the portal + a recipient-side confirmation loop ("I have updated my provincial file on my federal status"). The September 2025 Alberta CDB-deadline panic was almost entirely this category — a confirmation loop in the portal would have prevented most of it.

### 3. Hypothetical — "what if" planning

Decision-support questions about scenarios.

- "If I take this part-time job, what happens to my benefits?"
- "If I move out of province for 3 months?"
- "If I switch programs, what changes?"

**Why current channels fail.** Phone trees triage to categories, not scenarios. Workers don't always have time to run hypotheticals. Letters can't deliver personalized scenario answers.

**Best resolution.** Calculators or simulators in the portal. Not messaging.

### 4. Procedural confirmation — "did I do it right?"

Pre- and post-action questions.

- "Has my form been received?"
- "Did I submit the right thing?"
- "What happens now that I've reported this change?"

**Why current channels fail.** Recipients want fast confirmation; phone queues are slow; mail is days later. Documented as a major source of repeat phone calls.

**Best resolution.** Receipt confirmations + visible status. Inline acknowledgement after every action, not a separate channel.

### 5. Helper / delegated-authority context

Questions asked by someone acting on behalf of a recipient.

- "I'm acting as my brother's financial administrator — I need to know X about his file."
- "I have power of attorney for my mother — how do I update her address?"
- "My adult son is on this program — can I see his status?"

**Why current channels fail.** Phone agents have to re-verify the delegation every call. Existing channels aren't designed for delegated inquiry. Policy frameworks often recognize the role (trustees, FAs, attorneys under POA, ISC-appointed administrators), but the channels haven't caught up.

**Best resolution.** Role-aware portal access via a delegated-authority service. Phone agents would also benefit from a shared authority record they can consult.

### 6. Situational triage — "I'm in this specific situation"

Acute, specific, often urgent.

- "I'm being evicted, what help is there?"
- "My utility was disconnected."
- "I'm escaping domestic abuse."
- "I can't afford food this month."

**Why current channels fail.** Categorical phone trees can't route well. Recipients often end up in the wrong queue, get bounced between agents, or give up.

**Best resolution.** Triaged messaging with situational routing — not a categorical phone tree. Situation-based intake that flags urgency.

## Re-framing "secure messaging" as three products, not one

The "give me a way to ask a question" need is commonly scoped as a single inbox feature. That conflates three distinct products:

| Product | Serves categories | What it actually is |
|---|---|---|
| **Self-service data exposure** | 1 (about-me), 4 (procedural confirmation) | Status surfaces, receipts, decision rationale shown inline. Not messaging. |
| **Decision-support tools** | 3 (hypothetical) | Calculators, scenario explainers, simulators. Not messaging. |
| **Triaged messaging** | 2 (cross-system), 5 (helper context), 6 (situational) | Actual two-way channel that's role-aware and routes by situation. |

A team designing "secure messaging" as a single inbox is likely underserving categories 1, 3, and 4 because those need different products entirely.

## Evidence base

- Public discourse — CBC, Alberta Doctors' Digest, regional press, op-eds
- Advocacy organizations — Inclusion Alberta, Voice of Albertans with Disabilities, Friends of Medicare
- Alberta Ombudsman case summaries — AISH overpayment forgiveness, appeals duty-of-fairness
- Specific case study: September 2025 CDB-deadline panic (well-documented, required ministerial walkback)
- IVR call-volume signal: thousands of payment-related calls per month, indicating high volume of category 1 questions
- AISH Policy Manual — third-party authorization rules, channels of inquiry

## Caveats

- **Selection bias.** Public discourse skews toward acute, advocacy-flagged, or media-worthy situations. Mundane high-volume questions (next payment date, address change) don't show up in discourse because they're not worth posting about. The IVR-volume signal partly compensates.
- **Contact-centre data would sharpen this.** Call-reason data and IVR menu-selection data, if available, would calibrate the relative volume of each category for the specific program being scoped.
- **Population-specific weights.** These categories surfaced from AISH/ADAP analysis. Other programs may have different category distributions — the categories themselves likely generalize, but their weights don't. Validate against the specific program's recipient population.
- **The "helper context" category may be smaller or larger** depending on the program. AISH/PDD have high helper-layer presence because of recipient cognitive and disability profiles. Other programs (e.g., a permit renewal) may have negligible helper presence.

## Guidance for an agent using this

When a user asks about scoping a portal, a contact centre, an inquiry product, or messaging features:

1. **Don't accept "build secure messaging" as a single deliverable** without asking which categories it's meant to serve. If it's mostly category 1 (about-me), the right answer is data exposure, not messaging.
2. **Surface the cross-system category early.** It's the most common source of high-visibility recipient panic (e.g., the CDB-deadline case) and the easiest to underweight because the program team doesn't naturally think about *other* programs.
3. **Treat hypothetical questions as a decision-support need, not an inquiry need.** Calculators belong in the product spec, not in a messaging backlog.
4. **Ask about helper-layer prevalence in the recipient population.** If significant, role-aware access becomes a load-bearing requirement. If negligible, treat as P2 or omit.
5. **Acknowledge the selection bias** — what surfaces in discourse is not necessarily what's most common. Press for contact-centre data if you're using these categories for sizing decisions.

---

*Compiled from a Service Design Discovery session on the Alberta Disability Income Assistance program. See companion artifacts for full evidence trail.*
