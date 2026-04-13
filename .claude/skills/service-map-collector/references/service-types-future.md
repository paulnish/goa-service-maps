# Common Service Types — Deferred Design Note

**Status:** DEFERRED. Do not implement yet.
**Revisit when:** (a) all Alberta ministries are complete, or (b) we begin cross-jurisdictional analysis (e.g., adding BC or federal).
**Captured:** 2026-04-09

---

## Why this matters

The structure of a service doesn't change often. Unless the policy intent changes — unless the service starts doing something fundamentally different — the basic structure stays stable. What *does* change, sometimes dramatically, is how the service gets delivered: the channels, forms, URLs, org charts, and even the legislation underneath.

This gives us a useful layer the current schema doesn't capture. If we can name a service's *type*, we can say things about:

- The building blocks that should underpin it
- The parts that tend to work well or not work well
- The likely goals and policy intent behind it
- The outcomes users should expect

A service type is the most stable thing about a service. Everything else is implementation.

## The framework (Kate Tarling — Common Service Types)

1. **Registering, providing or reporting information.** Reporting financial fraud, filing company accounts, registering to vote, incorporating a business. Sometimes overlaps with Getting permission.

2. **Requesting, sharing or checking information.** Searching land titles, checking exam results, accessing birth records, checking your right to work.

3. **Paying for something.** Taxes, parking and traffic fines. Often appears as part of another service rather than a distinct thing. Filing an income tax return arguably fits best under Reporting information even though it usually includes payment.

4. **Getting financial support or claiming something.** Income support benefits, business grants, student loans.

5. **Getting permission to do something.** Moving livestock, fishing, driving or parking a car. Covers everything called a licence, permit, authority, visa, exemption, certificate, authorization, accreditation, or managed privilege.

6. **Scheduling something.** Arranging prison visits or medical appointments. Sometimes scheduling is part of another service; sometimes (like prison visits) it's significant enough to stand alone.

7. **Buying or ordering something.** Buying a house, or — more niche in government — ordering goods as part of an organization's commercial activities.

8. **Becoming something.** An electrician, a driver, a teacher. Includes apprenticeships, training, and continuing professional development (becoming a better version of something). Some prefer to file these under "Learning something." Often overlaps with Getting permission.

9. **Protecting something.** Public safety, civil liberties, children.

## How this could connect to the existing schema

The service types are **orthogonal** to the current hierarchy. Goals describe *why* a ministry does something; service types describe *what kind of thing* each service actually is. A single main service like "Operate Alberta's driver licensing system" decomposes into several types at once — Getting permission (issue the licence), Paying for something (fees), Requesting information (check status), Becoming something (learner → full driver), and Protecting something (road safety as policy intent).

Tagging services with a type would unlock things we can't do today:

- **Predict expected building blocks.** A Getting permission service should have an application channel, a decision/adjudication step, an appeals path, and usually a fee. If any are missing, the service definition is probably incomplete.
- **Spot suspicious gaps.** A Paying for something service with no `ch-transact` channel is almost certainly wrong.
- **Group services across ministries.** "Show me every Getting permission service in the GoA" becomes a real query.
- **Seed skill prompts differently by type.** During a ministry deep dive, the skill could ask different questions depending on what kind of service it's capturing.

## Open questions to answer before implementing

These are the decisions we parked:

1. **Where should the type live?** Options:
   - A single `service_type` field on each supporting service
   - An array, since some services legitimately straddle types (tax filing = Reporting + Paying)
   - At the main-service level rather than the supporting level

2. **How deep should this go?**
   - A classification tag displayed in the UI (new filter, like channels and user groups), or
   - Purely an authoring/validation aid for the skill — no UI change, just better data-gathering and validation

3. **Should expected building blocks be encoded formally?**
   - A reference doc per service type that says, e.g., "for Getting permission services, check for: application channel, decision mechanism, fee, appeals, renewal."
   - That would turn each type into a validator checklist during ministry deep dives.

4. **Where should the canonical list of types live?**
   - `config.json` per jurisdiction (so BC or federal could adapt the list), or
   - A reference file in the skill itself (universal across jurisdictions)
   - Lean: skill reference, because the types are a framework concept, not a jurisdiction-specific taxonomy. Worth confirming when we pick this up.

## When we revisit

Two good moments to reopen this:

- **After all Alberta ministries are captured.** We'll have a large enough sample to test whether the nine types actually cover every GoA service, and whether any services need multi-type tagging in practice.
- **When we start a second jurisdiction.** Cross-jurisdictional comparison is exactly where service types earn their keep — they let you compare "all Getting permission services" across AB, BC, and the feds without getting tangled in org-chart or legislation differences.

At that point: answer the four open questions, then decide whether to add a field to the schema, a reference doc to the skill, or both.
