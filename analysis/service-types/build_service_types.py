#!/usr/bin/env python3
"""
Phase 4: Build service_types.json from phase-1-classification.json.

For each of the 14 curated service types from phase-2-clusters.md, assigns matching
services from the corpus by name pattern + primary_task constraint. Verifies the
leverage bar (5+ services across 3+ ministries) mechanically. Generates the final
JSON artifact at goa-service-maps/data/ab/service_types.json.

Hand-authored content (shared_shape, variations, gaps, proposed_examples) is loaded
from this file; mechanical content (services list, leverage stats, kate_tarling tags)
is derived from the corpus.

Run:
  python3 build_service_types.py        # generates artifact at goa-service-maps path
  python3 build_service_types.py --dry  # prints summary without writing

Output:
  goa-service-maps/data/ab/service_types.json
  phase-4-uncategorised.txt (any services that didn't match any type — flag for review)
"""

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
CLASSIFICATION = ROOT / "phase-1-classification.json"
# Output writes to the canonical jurisdiction data folder, relative to this repo.
REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_PATH = REPO_ROOT / "data" / "ab" / "service_types.json"
UNCATEGORISED = ROOT / "phase-4-uncategorised.txt"

KATE_TARLING_INTENTS = [
    {"id": "registering-information", "name": "Registering, providing or reporting information"},
    {"id": "checking-information", "name": "Requesting, sharing or checking information"},
    {"id": "paying", "name": "Paying for something"},
    {"id": "financial-support", "name": "Getting financial support or claiming something"},
    {"id": "permission", "name": "Getting permission to do something"},
    {"id": "scheduling", "name": "Scheduling something"},
    {"id": "buying", "name": "Buying or ordering something"},
    {"id": "becoming", "name": "Becoming something"},
    {"id": "protecting", "name": "Protecting something"},
]

SERVICE_TASKS = ["Apply", "Transact", "Check", "Report", "Engage", "Find", "Advise"]


def matches_apply_benefit(s):
    """apply-for-a-benefit: financial-support intent, person-shaped means/categorical benefits.
    Also catches claim-shaped variants (event-triggered: insurance, disaster, damage)."""
    if s["primary_task"] not in ("Apply", "Transact"):
        return False
    name = s["name"].lower()
    keywords = [
        # Person-shape benefits
        "income support", "financial help", "financial support", "financial assistance",
        "monthly financial support", "monthly support",
        "severe disability", "aids to daily living",
        "child care subsidies", "childcare subsidy", "child care subsidy",
        "drug benefit", "drug coverage", "health coverage",
        "dental, optical", "dental and optical",
        "prescription drug", "remote area heating", "heating allowance",
        "student loan", "student loans and grants",
        "escaping abuse", "low-income transit",
        "appliance and health costs", "wage top-up",
        "developmental disabilities", "service dog",
        "foundational learning assistance", "employment skills training",
        "post-secondary education after care",
        "FSCD", "fscd",
        "support for your child with a disability",
        "help adapting or repairing your home",
        "deferring property", "defer property",
        "tax credit", "tax exemption", "tax relief",
        # Claim-shape variants (event-triggered)
        "insurance",  # crop, hail, livestock price, AB Indian Tax Exemption, etc.
        " a claim", "compensation claim",
        "disaster recovery", "wildlife damage",
        "claim under", "warranty program",
        "pension plan claim",
        # Educational enrolment-as-benefit
        "enrol in income", "enrol your child in school",
        "enrol in distance",
        "post-secondary institution",
        "matched farm savings",
        # Other benefit-shaped
        "guarantee", "fee waiver", "fee exemption",
        "court filing fee",
        "reimbursed", "restitution", "victim",
        "homelessness", "housing partnership funding",
        "housing capital funding", "lodge",
        "indigenous housing",
        # Legal aid and family support orders (financial support shape)
        "legal aid",
        "child or spousal support",
        "automatic child support",
        "support order",
        # Treatment-as-benefit
        "long-term residential treatment",
        "recovery community",
        # Indigenous-targeted supports
        "indigenous business investment",
        "indigenous workers",
        "indigenous community broadband",
        "land allocation",
        # Other claim-shape
        "claim jury duty",
        "unclaimed property",
        # Matched-savings benefit
        "government-matched farm savings",
    ]
    return any(k in name for k in keywords)


def matches_apply_grant(s):
    """apply-for-a-grant-or-funding: financial-support, project/org-shaped."""
    if s["primary_task"] != "Apply":
        return False
    name = s["name"].lower()
    keywords = [
        "grant", "funding", "tax credit", "tax exemption",
        "scholarship", "award", "loan", "research and commercialization",
        "matched farm savings",
    ]
    excludes = [
        "student loan",  # those are individual-shape benefits
        "student loans and grants",
        "escaping abuse",  # benefit, not grant
    ]
    if any(e in name for e in excludes):
        return False
    return any(k in name for k in keywords)


def matches_apply_licence(s):
    """apply-for-a-licence-or-permit: permission intent (including becoming for personal credentials).
    Also catches: immigration streams, quotas, passes, qualifications recognition, classifications."""
    if s["primary_task"] not in ("Apply", "Transact"):
        return False
    name = s["name"].lower()
    keywords = [
        "licence", "license", "permit", "certificate", "certification",
        "authorization", "designation", "approval", "registration as a",
        "stream",  # immigration: Express Entry, Opportunity Stream, etc.
        "express entry",
        "membership in",  # Métis Settlement
        "become a wildland firefighter", "become a foster", "become a commissioner",
        "appointment as a notary",
        "qualifications assessed", "credential recognized", "trade credential",
        "recognized",
        "for classification",  # film/video classification
        "operate a shooting club",
        "transfer teaching",
        "quota", "lands camping pass", "park conservation pass",
        "ignition interlock",
        "research permit",
        # Get + credential variants in Transact task
        "get a commercial driver",
        "get a driver's abstract",
        "get an in-transit",
        "get certified as",
        "start or buy a business",  # immigration entrepreneur
        "buy a business in alberta",
        "entrepreneur",
    ]
    excludes = [
        "search land title",
    ]
    if any(e in name for e in excludes):
        return False
    return any(k in name for k in keywords)


def matches_register_something(s):
    """register-something: registering-information + becoming."""
    if s["primary_task"] != "Apply":
        return False
    name = s["name"].lower()
    return (
        name.startswith("register")
        or "register a marriage" in name
        or "and register" in name  # "Make and register a personal directive"
        or name.startswith("submit a film or video for classification")  # registry-of-classifications
    )


def matches_pay_fee_fine(s):
    """pay-a-fee-or-fine: paying intent."""
    if s["primary_task"] != "Transact":
        return False
    name = s["name"].lower()
    return name.startswith("pay") or "and pay" in name or "pay a" in name or "pay or dispute" in name


def matches_renew(s):
    """renew-something: permission renewal. Must be the action of renewing, not a program
    name with 'renewal' in it (e.g. 'Renewal Stream' or 'capital renewal funding')."""
    name = s["name"].lower()
    return name.startswith("renew ") or " or renew " in name or " or renew." in name or name.endswith(" or renew")


def matches_check_status(s):
    """check-status-or-records: checking-information, authenticated lookup of own records."""
    if s["primary_task"] != "Check":
        return False
    return True  # all Check task services are check-status-or-records candidates


def matches_report_concern(s):
    """report-a-concern-or-incident: protecting, citizen pushes info about hazard/third-party."""
    if s["primary_task"] != "Report":
        return False
    name = s["name"].lower()
    # Distinguish from file-a-complaint
    if name.startswith("file") or name.startswith("make a complaint") or name.startswith("submit a complaint"):
        return False
    return True


def matches_file_complaint(s):
    """file-a-complaint: protecting, formal complaint about regulated party.
    Cross-task because the same shape appears in both Report (channel-based) and Apply
    (when the complaint is filed via ch-apply digital form). Service type stays Report-shape."""
    name = s["name"].lower()
    return (name.startswith("file") and ("complaint" in name or "grievance" in name)) or \
           "make a complaint" in name or "submit a complaint" in name


def matches_find_service_place(s):
    """find-a-service-or-place: checking-information, find a provider/place."""
    if s["primary_task"] != "Find":
        return False
    name = s["name"].lower()
    if not name.startswith("find"):
        return False
    keywords = [
        "doctor", "provider", "hospital", "clinic", "service",
        "centre", "shelter", "library", "office", "professional",
        "advisor", "mentor", "victim services", "settlement services",
        "near you", "near me", "in your community", "near a",
        "treatment", "facility", "agency", "authority",
        "regulated forestry", "licensed addiction",
    ]
    return any(k in name for k in keywords)


def matches_search_register(s):
    """search-a-public-register: checking-information, validation/lookup."""
    name = s["name"].lower()
    keywords = [
        "search", "look up", "verify", "check whether", "check if",
        "check your eligibility", "check broadband",
        "check flood maps", "check surgical", "check the status of",
        "check public land", "check current fire",
        "check your carrier", "check assessment results",
        "check highway", "check road",
    ]
    if not any(k in name for k in keywords):
        return False
    # Exclude pure "find a doctor" etc which is service/place
    excludes = ["find a", "doctor", "provider", "service near"]
    if any(e in name for e in excludes):
        return False
    return s["primary_task"] in ("Find", "Transact", "Check")


def matches_read_information(s):
    """read-information-or-guidance: any Find task service that doesn't match find-a-service-or-place
    or search-a-public-register. Acts as the Find sink. Most Find services are content-shaped:
    citizens read about a topic, regulation, right, or program. Lowest design system value because
    it's content/IA territory rather than action design, but still ~13-15% of the corpus."""
    if s["primary_task"] != "Find":
        return False
    return True  # Find sink — claims everything in Find that earlier types didn't take.


def _matches_read_information_keywords_unused(s):
    """Kept for reference — earlier keyword-based matcher. Replaced by the sink approach
    above because Find services use too many verbs to enumerate cleanly."""
    name = s["name"].lower()
    keywords = [
        "learn about", "learn how", "access information", "access health",
        "access market", "access government publications",
        "access royalty", "access oil", "access methane",
        "access language", "access financial literacy",
        "access addiction", "access reintegration", "access cybersecurity",
        "access supports for", "access technical standards",
        "access forest", "access outdoor",
        "access wildfire", "access water quality",
        "access drought", "access environmental",
        "access air", "access reconciliation",
        "access employment and training", "access consultation",
        "access fasd", "access affordable", "access indigenous",
        "access lodge", "access capital",
        "access provincial archives", "access french-language",
        "access supervised drug",
        "access information about",
        "view ", "read ", "see how", "see upcoming", "see what's planned", "see where",
        "explore career", "explore decision",
        "explore lithium", "explore careers",
        "find information", "find road safety",
        "find resources", "find ways to reduce",
        "find curriculum", "find continuing care",
        "find healthy aging", "find affordable",
        "find out what", "find international",
        "get information", "get advice",
        "get crop disease", "get farm water",
        "get guidance", "get help expanding",
        "get help if", "get help finding a job",
        "get help preparing court forms",
        "get free family law information",
        "get connected", "get emergency preparedness information",
        "subscribe", "receive emergency",
        "complain about", "complain about treatment",
        "review capital plan",
        "understand or participate in a municipal",
        "navigate the licensing",
        "verify a health professional",
        "comply with",
        "borrow for municipal",
        "pay timber dues",
        "practise safe",
        "help with wildfire",
        "invest in alberta",
        "propose an all-season",
        "control noxious",
        "connect with",
        "appeal",  # appeals are in their own type, but if they leak here as Find, catch them
    ]
    return any(k in name for k in keywords)


def matches_access_in_person(s):
    """access-an-in-person-program: any Advise task service.
    Acts as the Advise sink. The unifying property is: the citizen has no digital action
    surface for this service today — it's delivered through phone, in-person, mail, or email
    only. The design system can't help build a digital implementation until digitization
    decisions happen. Some are intrinsically in-person (emergency shelter); some are
    Apply-shape services that haven't been digitized (vehicle inspection, regulatory
    compliance, transfer ownership). Brief 07 should surface this category as a
    digital-readiness gap, not a design system gap."""
    return s["primary_task"] == "Advise"


def matches_appeal(s):
    """appeal-a-decision: extension to Kate Tarling's nine."""
    name = s["name"].lower()
    return name.startswith("appeal")


def matches_request_government_records(s):
    """request-government-action-or-records: formal request to government for records, info,
    review, or specific action (FOI, privacy info request, request a fatality inquiry,
    request a review). Distinct from search-a-public-register because the citizen submits
    a formal request rather than querying a public database — there's a process, not just
    a lookup. Distinct from apply-for-a-benefit because no eligibility/decision/payment shape;
    distinct from file-a-complaint because no regulated party / investigation."""
    name = s["name"].lower()
    keywords = [
        "freedom of information request",
        "request your own personal information",
        "request information about a partner",  # Clare's Law
        "request a public fatality inquiry",
        "request a review of a lawyer",
        "request death investigation documents",
        "request civil claims mediation",
        "request victim restitution",
        "request a heritage resource impact assessment",
        "request a copy of a collision report",
        "submit a community impact statement",
        "submit a victim impact statement",
        "submit a consultation assessment request",
        "request a capacity assessment",
    ]
    return any(k in name for k in keywords)


# Service type definitions. Order matters — first matching rule wins.
SERVICE_TYPES = [
    {
        "id": "appeal-a-decision",
        "name": "Appeal a decision",
        "service_task": "Apply",  # multi-task in reality; default to Apply for shape similarity
        "kate_tarling_intents": ["checking-information", "protecting"],
        "value_weight": "medium",
        "value_weight_rationale": "Reach: low but high need when invoked. Citizens' safety net when initial decisions go wrong.",
        "is_extension": True,
        "extension_note": "Not in Kate Tarling's original nine. Surfaced empirically — multiple ministries have explicit 'Appeal a...' services with a recognisable shape (request review, submit grounds, reconsideration or hearing, new decision). Recommend adding to the GoA's working vocabulary.",
        "shared_shape": "Citizen references a prior decision they want overturned, submits grounds (procedural error, new evidence, wrong on the merits), waits for review by a separate body, receives a new decision (uphold, overturn, or remit). The appellant is heard but doesn't drive the process.",
        "variations": "Administrative appeals (benefits, planning, safety codes) vs. judicial appeals (court decisions). Some go to a separate tribunal, some loop within the same regulator.",
        "product_types_used": ["public-form"],
        "matcher": matches_appeal,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "review-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-long-answer-question-with-a-maximum-word-count",
            "expand-or-collapse-part-of-a-form",
        ],
        "gaps": [
            {"text": "No reference-the-original-decision pattern. Appeals start with a specific prior decision and need to link/summarise it."},
            {"text": "No grounds-for-appeal composer. Appeals need structured reason categories (procedural, factual, new evidence).",
             "cross_cutting_refs": ["describe-what-happened"],
             "flavor_note": "Grounds for appeal: structured event-by-event reasoning, often referencing the original decision's facts."},
            {"text": "No appeal-status-tracking pattern.",
             "cross_cutting_refs": ["status-tracking"],
             "flavor_note": "Distinct appeal milestones; three-branch outcome ahead."},
            {"text": "No appeal-outcome-with-action pattern (uphold/overturn/remit branches).",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Appeal-outcome variant of results: three-branch decision (uphold/overturn/remit)."},
        ],
        "proposed_examples": [
            {"concept": "Appeal initiation",
             "rationale": "Loads the original decision, lets the appellant select grounds and write reasoning."},
            {"concept": "Appeal status",
             "rationale": "Status tracker variant for appeals; differs from application status because the next steps and timelines are different.",
             "cross_cutting_refs": ["status-tracking"],
             "flavor_note": "Appeal-specific milestones (filed → admitted → heard → decided); three-branch outcome ahead."},
            {"concept": "Appeal outcome letter",
             "rationale": "Decision letter pattern with the three possible branches.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Appeal-outcome variant of results: three-branch (uphold/overturn/remit) with reasoning."},
        ],
    },
    {
        "id": "request-government-action-or-records",
        "name": "Request government records or action",
        "service_task": "Apply",  # Most are Apply-task; some are Find/Transact/Advise. Multi-task in reality.
        "kate_tarling_intents": ["checking-information", "protecting"],
        "value_weight": "medium",
        "value_weight_rationale": "Reach: medium (thousands of FOI requests, lawyer reviews per year). Need: democratic accountability and personal records access.",
        "shared_shape": "Citizen submits a formal request for government records, information, or specific action (inquiry, mediation, restitution, impact statement). Triage and acceptance, processing by the appropriate body, response or release issued. Distinct from search-a-public-register because there's a process; distinct from apply-for-a-benefit because no eligibility/payment shape.",
        "variations": "Information requests (FOI, your own personal records) vs. specific-action requests (fatality inquiry, lawyer fee review, mediation) vs. participation requests (community/victim impact statements). Most are JUS-led; CPE/SA handle FOI; INFRA, TEC have niche request paths.",
        "product_types_used": ["public-form"],
        "matcher": matches_request_government_records,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-user-for-an-address",
            "ask-a-long-answer-question-with-a-maximum-word-count",
            "ask-a-user-for-a-birthday",
        ],
        "gaps": [
            {"text": "No request-form pattern with required-info checklist (most have specific data needs)."},
            {"text": "No status-of-request pattern. Many requests have legislated timelines (FOI is 30 days). Citizens need to track.",
             "cross_cutting_refs": ["status-tracking"],
             "flavor_note": "Legislated timeline surfaced (FOI 30 days); status step must include the deadline."},
            {"text": "No release-of-records pattern. After approval, the citizen receives the records — what does that page look like?",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Records-release variant of results: includes the records themselves with redaction explanation if applicable."},
        ],
        "proposed_examples": [
            {"concept": "Records request form",
             "rationale": "Form with required information checklist plus optional fields, fee handling, and consent."},
            {"concept": "Request status with timeline",
             "rationale": "Status page that surfaces the legislated timeline (e.g. FOI 30 days) and current step.",
             "cross_cutting_refs": ["status-tracking"],
             "flavor_note": "Legislated-timeline flavor: surfaces the statutory deadline alongside current step."},
            {"concept": "Released records view",
             "rationale": "Page or download experience for the released records, with redaction explanation if applicable.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Records-release variant: the outcome IS the records, with redaction explanation."},
        ],
    },
    {
        "id": "file-a-complaint",
        "name": "File a complaint",
        "service_task": "Report",
        "kate_tarling_intents": ["protecting"],
        "value_weight": "medium",
        "value_weight_rationale": "Reach: medium. Need: regulatory accountability matters but not life-or-death.",
        "shared_shape": "Citizen files a formal complaint about a regulated party (professional, business, government decision-maker). Triage and acceptance, investigation by the regulator, decision communicated, possible appeal path. The complainant is heard but doesn't drive the process.",
        "variations": "Regulated-profession complaints (health, security, locksmith) vs. business marketplace complaints (consumer protection) vs. systemic complaints (human rights, police conduct, privacy) vs. specific party (guardian/trustee). Investigation rigour varies.",
        "product_types_used": ["public-form"],
        "matcher": matches_file_complaint,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "review-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-user-for-an-address",
            "ask-a-user-for-a-birthday",
            "ask-a-long-answer-question-with-a-maximum-word-count",
            "give-more-information-before-asking-a-question-a",
            "give-more-information-before-asking-a-question-b",
        ],
        "gaps": [
            {"text": "No 'describe what happened' pattern with timeline support. Complaints often need a sequence of events.",
             "cross_cutting_refs": ["describe-what-happened"],
             "flavor_note": "Complaint timeline: event-by-event with dates, often spanning months."},
            {"text": "No regulated-party-search pattern. The citizen is filing against a regulated party — they need to find/identify that party.",
             "cross_cutting_refs": ["look-up-and-pick"],
             "flavor_note": "Embedded lookup inside the complaint flow: search the doctor / business / officer registry to identify the target of the complaint."},
            {"text": "No status-update notification pattern. Investigations take months.",
             "cross_cutting_refs": ["service-messages", "status-tracking"],
             "flavor_note": "Long-running investigation: periodic status updates over months."},
            {"text": "No outcome-letter pattern (current result-page is too thin for complaint outcomes).",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Decision-letter variant for complaints: long-form reasoning, next steps, appeal info."},
            {"text": "No appeal-pathway pattern (overlaps with appeal-a-decision)."},
        ],
        "proposed_examples": [
            {"concept": "Identify the regulated party",
             "rationale": "Search-and-select for finding the doctor / business / officer the complaint is about.",
             "cross_cutting_refs": ["look-up-and-pick"],
             "flavor_note": "Regulated-party lookup as an in-flow step before the complaint narrative."},
            {"concept": "Timeline-of-events composer",
             "rationale": "Section pattern for ordered narrative input.",
             "cross_cutting_refs": ["describe-what-happened"],
             "flavor_note": "Complaint flavor: events spanning months, often with dates and witnesses."},
            {"concept": "Investigation status updates",
             "rationale": "Long-running status surfacing; overlaps with check-status-or-records.",
             "cross_cutting_refs": ["status-tracking"],
             "flavor_note": "Long-running flavor: monthly-scale status updates over the investigation lifespan."},
            {"concept": "Decision letter view",
             "rationale": "Long-form decision page with reasoning, next steps, and appeal info.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Decision-letter variant: reasoning + next steps + appeal pathway."},
        ],
    },
    {
        "id": "report-a-concern-or-incident",
        "name": "Report a concern or incident",
        "service_task": "Report",
        "kate_tarling_intents": ["protecting"],
        "value_weight": "high",
        "value_weight_rationale": "Need: safety-critical (child abuse, wildfire, animal disease reports). Downstream costs of unreported incidents are high.",
        "shared_shape": "Citizen pushes information about a hazard, suspected harm, or third-party concern. No assessment of the citizen's eligibility — the service is the act of reporting. Acknowledgment is usually sent; investigation may follow with no further citizen involvement.",
        "variations": "Safety hazards (road, fire, wildlife) vs. abuse/harm reports (child, elder, workplace) vs. environmental incidents (substance release, emissions exceedance) vs. property issues. Some are time-critical.",
        "product_types_used": ["public-form"],
        "matcher": matches_report_concern,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-user-for-an-address",
            "ask-a-user-for-a-birthday",
            "add-another-item-in-a-modal",
            "show-a-list-to-help-answer-a-question",
        ],
        "gaps": [
            {"text": "No anonymous-reporting affordance. Many reports allow or require anonymity."},
            {"text": "No report-receipt-with-reference-number pattern. Reporters need a way to follow up.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Submission-receipt variant: light content, reference number, what-happens-next, contact path."},
            {"text": "No file-evidence-with-context pattern.",
             "cross_cutting_refs": ["submit-supporting-documents"],
             "flavor_note": "Report-evidence flavor: each piece of evidence attached to a specific fact in the report."},
            {"text": "No urgency-routing pattern. Some reports are time-critical (animal disease, wildfire)."},
        ],
        "proposed_examples": [
            {"concept": "Optional-identity report form",
             "rationale": "Pattern showing the anonymous/named branch with consequence framing."},
            {"concept": "Report receipt with reference number",
             "rationale": "Page showing reference number, what happens next, contact path.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Submission-receipt variant for reports."},
            {"concept": "Evidence-attached-to-fact composer",
             "rationale": "Section pattern for uploading evidence linked to specific report items.",
             "cross_cutting_refs": ["submit-supporting-documents"],
             "flavor_note": "Evidence-with-context flavor: uploads tied to specific facts in the report narrative."},
        ],
    },
    {
        "id": "register-something",
        "name": "Register something",
        "service_task": "Apply",
        "kate_tarling_intents": ["registering-information", "becoming"],
        "value_weight": "high",
        "value_weight_rationale": "Reach: high (vehicle, business, birth, marriage registrations). Need: high (required for daily life). Anchors the short-form productType candidate.",
        "intent_note": "Multi-intent. Vehicle/business/birth registrations are registering-information; apprentice/professional registrations are becoming.",
        "shared_shape": "Citizen or business submits identifying information, system validates basic eligibility (no full assessment), registry entry created, confirmation issued with a registration number. Often ongoing — registry must be kept current.",
        "variations": "Vital records (birth, marriage, death) vs. property records (vehicle, land, lien) vs. credentials (apprentice, regulated professional) vs. business identity (corporation, tourism levy collector).",
        "product_types_used": ["public-form"],
        "matcher": matches_register_something,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-user-for-a-birthday",
            "ask-a-user-for-an-address",
            "select-one-or-more-from-a-list-of-options",
        ],
        "gaps": [
            {"text": "No short-form (multi-fields-per-page) registration pattern. Public-form is one-question-per-page which is overkill for short registrations."},
            {"text": "No registry-confirmation receipt pattern. Result-page is decision-shaped (approved/denied); registrations should show the registry entry that was created.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Registry-receipt flavor: hybrid of submission-receipt and issued-credential — confirms creation AND shows the new registry entry with ID and downloadable record."},
            {"text": "No update-existing-registration pattern. Registries are alive — change of address, name change after marriage.",
             "cross_cutting_refs": ["my-account", "look-up-and-pick"],
             "flavor_note": "Update-existing flow: look up your registry entry → modify → confirm → updated-record-receipt."},
        ],
        "proposed_examples": [
            {"concept": "Compact form page",
             "rationale": "Multi-field registration form (12-20 fields) on one or two pages, denser than public-form per-idea pattern. Anchors the `short-form` productType candidate."},
            {"concept": "Registry receipt",
             "rationale": "Page showing the created record with ID, key facts, downloadable PDF, follow-on actions.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Registry-receipt flavor of results: confirms creation AND shows the new entry."},
            {"concept": "Update an existing record",
             "rationale": "Look-up → modify → confirm → updated-record-receipt flow.",
             "cross_cutting_refs": ["look-up-and-pick", "my-account"],
             "flavor_note": "Update-existing flow: starts with lookup of citizen's existing registry entry, ends in a refreshed registry-receipt."},
        ],
    },
    {
        "id": "apply-for-a-licence-or-permit",
        "name": "Apply for a licence or permit",
        "service_task": "Apply",
        "kate_tarling_intents": ["permission", "becoming"],
        "value_weight": "high",
        "value_weight_rationale": "Reach: high (driver's licences alone touch millions; plus professional, business, activity permits). Need: high (daily-life-critical credentials).",
        "intent_note": "Multi-intent. Personal credentials (teacher certification, PAL) lean becoming; business licences and activity permits lean permission.",
        "shared_shape": "Citizen or business demonstrates qualification (training, fitness, fee paid, premises inspected), submits application with evidence, waits for decision, receives credential with expiry and conditions. Renewal is a lighter version of the same shape — verify identity and continued eligibility, pay fee, get updated expiry.",
        "variations": "Personal credentials (driver's licence, firearms PAL, professional licences) vs. business credentials (cannabis, security, locksmith) vs. activity permits (timber, fire, oversize load). **Renewal** is a recurring sub-shape: 'Apply for or renew' services (gaming/liquor/cannabis, driver's licence) and standalone 'Renew' services (firearms PAL) follow the same flow as the original application but pre-filled — fewer questions, focus on what's changed.",
        "product_types_used": ["public-form"],
        "matcher": matches_apply_licence,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "task-list-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "review-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-user-for-an-address",
            "ask-a-user-for-a-birthday",
            "expand-or-collapse-part-of-a-form",
        ],
        "gaps": [
            {"text": "No declaration/attestation pattern. Most licences require the citizen to declare facts under penalty."},
            {"text": "No fitness-or-qualifications composer. Permits often require proof of training, experience hours, supervisor sign-off."},
            {"text": "No fee-with-application pattern. Many licences require payment at submission.",
             "cross_cutting_refs": ["payment"],
             "flavor_note": "Payment coupled with application submission (not a standalone pay flow)."},
            {"text": "No outcome-with-credential view. result-page exists but no example of 'here's your decision and your printable/wallet credential.'",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Issued-credential variant of results: outcome plus the granted credential with print/save/wallet affordances."},
            {"text": "**Renewal-specific:** No look-up-existing pattern. Renewal starts with verifying who you are and pulling up your existing record.",
             "cross_cutting_refs": ["look-up-and-pick"],
             "flavor_note": "Renewal-lookup flavor: authenticated lookup of the citizen's own existing licence as a renewal entry."},
            {"text": "**Renewal-specific:** No diff-from-current pattern. Renewal usually shows 'here's what we have on file; change anything?'"},
            {"text": "**Renewal-specific:** No renewal-reminder/notification pattern.",
             "cross_cutting_refs": ["service-messages"],
             "flavor_note": "Renewal-reminder flavor of service-messages: triggered by expiry approaching."},
        ],
        "proposed_examples": [
            {"concept": "Attestation / declaration",
             "rationale": "Section pattern with explicit affirmation, plain-language consequences, signature."},
            {"concept": "Qualifications composer",
             "rationale": "Section for showing training, hours, or external evidence."},
            {"concept": "Pay-and-submit",
             "rationale": "Coupled flow joining form review → payment → submission.",
             "cross_cutting_refs": ["payment"],
             "flavor_note": "Embedded-payment flavor: payment as the final step of an application submission."},
            {"concept": "Issued credential page",
             "rationale": "Page showing decision and credential with print/save/wallet-add affordances.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Issued-credential variant of results: includes the granted credential."},
            {"concept": "Verify-and-renew flow",
             "rationale": "Renewal sub-shape: authenticate → see current record → confirm or edit → pay → updated credential."},
            {"concept": "Renewal reminder",
             "rationale": "Email/notification template + landing page for the renewal start.",
             "cross_cutting_refs": ["service-messages"],
             "flavor_note": "Renewal-reminder flavor: triggered by expiry approaching; landing page resumes the renewal flow."},
        ],
    },
    {
        "id": "apply-for-a-grant-or-funding",
        "name": "Apply for a grant or funding",
        "service_task": "Apply",
        "kate_tarling_intents": ["financial-support"],
        "value_weight": "high",
        "value_weight_rationale": "Financial: hundreds of millions to billions/year. Reach: medium (more orgs than individuals).",
        "shared_shape": "Organization or project lead submits a proposal with budget, work plan, and outcomes; reviewed against program criteria; awarded with a contract or transfer payment agreement; ongoing reporting and accountability.",
        "variations": "Project grants (one-time, defined deliverables) vs. operating grants (ongoing, organizational support) vs. capital funding (infrastructure). Some are open-call competitive, some are formula-based.",
        "product_types_used": ["public-form"],
        "matcher": matches_apply_grant,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "task-list-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "review-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-user-for-dollar-amounts",
            "expand-or-collapse-part-of-a-form",
            "add-another-item-in-a-modal",
            "add-a-record-using-a-drawer",
        ],
        "gaps": [
            {"text": "No project-budget input pattern. Grant applications need structured cost tables."},
            {"text": "No multi-applicant/team pattern. Grants often need lists of project participants."},
            {"text": "No work-plan/milestone composer."},
            {"text": "No attachment manager. Grant applications often require multiple supporting documents.",
             "cross_cutting_refs": ["submit-supporting-documents"],
             "flavor_note": "Grant-application flavor: many documents (budget spreadsheet, project description, letters of support); checklist enforces required vs optional."},
            {"text": "No reporting-back flow (post-award), though that's worker-side and deferred."},
        ],
        "proposed_examples": [
            {"concept": "Budget table input",
             "rationale": "Section composer with itemized rows, categories, totals."},
            {"concept": "Project team composer",
             "rationale": "Pattern for adding multiple participants with their own form fields each."},
            {"concept": "Document checklist with upload",
             "rationale": "Pattern showing required attachments with status indicators.",
             "cross_cutting_refs": ["submit-supporting-documents"],
             "flavor_note": "Grant flavor: multiple documents with category and required/optional status."},
            {"concept": "Multi-organization profile",
             "rationale": "Section for the org submitting (their address, registration, history)."},
        ],
    },
    {
        "id": "apply-for-a-benefit",
        "name": "Apply for a benefit",
        "service_task": "Apply",
        "kate_tarling_intents": ["financial-support"],
        "value_weight": "high",
        "value_weight_rationale": "Reach: hundreds of thousands of Albertans (income support, AISH, childcare subsidy). Financial: billions/year paid. Need: people depend on these to live.",
        "shared_shape": "Citizen demonstrates eligibility (means-tested or categorical), provides personal/household info, uploads supporting documents, waits for adjudication, receives ongoing or one-time payment with a decision letter. Some have ongoing review cycles.",
        "variations": "Means-tested (income support, AISH, childcare subsidy) vs. categorical (seniors financial assistance, disability benefits). Some pay monthly, some are one-time. Includes claim-shaped variants triggered by events (disaster recovery, wildlife damage compensation).",
        "product_types_used": ["public-form"],
        "matcher": matches_apply_benefit,
        "existing_examples": [
            {"productType": "public-form", "slug": "start-page"},
            {"productType": "public-form", "slug": "task-list-page"},
            {"productType": "public-form", "slug": "question-page"},
            {"productType": "public-form", "slug": "review-page"},
            {"productType": "public-form", "slug": "result-page"},
        ],
        "interaction_examples": [
            "ask-a-user-for-an-address",
            "ask-a-user-for-a-birthday",
            "ask-a-user-for-direct-deposit-information",
            "ask-a-user-for-an-indian-registration-number",
            "ask-a-user-for-dollar-amounts",
            "expand-or-collapse-part-of-a-form",
            "reveal-input-based-on-a-selection",
            "form-stepper-with-controlled-navigation",
            "show-a-user-progress",
            "show-a-user-progress-when-the-time-is-unknown",
            "link-the-user-to-give-feedback-to-the-service",
        ],
        "gaps": [
            {"text": "No eligibility-check pattern. Citizens often need to know if they qualify before starting.",
             "cross_cutting_refs": ["eligibility-checking"],
             "flavor_note": "Benefit-eligibility flavor: income, household, residency questions yielding qualify/likely/unlikely."},
            {"text": "No means-test screen. Most Alberta benefits are means-tested; no example shows how to handle income+household+deductions in a form."},
            {"text": "No status-tracking page. The current result-page covers the immediate confirmation; nothing covers checking on a long-running decision.",
             "cross_cutting_refs": ["status-tracking"],
             "flavor_note": "Long-running benefit decision tracking with clarification-request branch."},
            {"text": "No clarification-request flow. When the worker side asks for more info.",
             "cross_cutting_refs": ["service-messages"],
             "flavor_note": "Worker-to-citizen clarification request: triggers a message and a landing page for upload/response."},
            {"text": "No save-and-return pattern. Means-tested applications are long; many citizens can't finish in one sitting.",
             "cross_cutting_refs": ["save-and-return"],
             "flavor_note": "Means-tested benefit forms: 30-60 minute completion time, often interrupted."},
        ],
        "proposed_examples": [
            {"concept": "Eligibility checker",
             "rationale": "Pre-form gate: answer 4-5 questions, get a yes/no/maybe with reasons.",
             "cross_cutting_refs": ["eligibility-checking"],
             "flavor_note": "Benefit-eligibility flavor: income/household/residency questions."},
            {"concept": "Status tracker",
             "rationale": "Page citizens visit after submitting to see where their application is. Phase 5 of Apply six-phase flow has no existing example.",
             "cross_cutting_refs": ["status-tracking"],
             "flavor_note": "Long-running benefit decision tracker; surfaces 'and now what?' affordances for clarification-request branch."},
            {"concept": "Means-test composer",
             "rationale": "Section that handles eligibility math (income, household, deductions) with explanatory help."},
            {"concept": "Save-and-return",
             "rationale": "Pattern for partial-fill state across sessions plus account-side pages.",
             "cross_cutting_refs": ["save-and-return"]},
            {"concept": "Respond to a clarification request",
             "rationale": "Page or flow citizen reaches via notification, lets them upload more info or answer follow-ups.",
             "cross_cutting_refs": ["service-messages"],
             "flavor_note": "Worker-to-citizen clarification flow: from notification → landing → upload/response → updated status."},
        ],
    },
    {
        "id": "pay-a-fee-or-fine",
        "name": "Pay a fee or fine",
        "service_task": "Transact",
        "kate_tarling_intents": ["paying"],
        "value_weight": "high",
        "value_weight_rationale": "Financial: billions/year (traffic fines, fuel tax, royalties). Reach: high (every fueling, every fine). Anchors the payment productType candidate.",
        "shared_shape": "Citizen receives or knows about an obligation (fine, fee, tax owed), looks up the amount, pays online with optional dispute path. Receipt issued; account updated.",
        "variations": "Penalties (traffic fines, impaired driving) vs. recurring payments (fuel tax, mineral rights tax) vs. one-off fees (court filing fee, royalty payments).",
        "product_types_used": [],
        "product_types_proposed": ["payment", "transaction"],
        "matcher": matches_pay_fee_fine,
        "existing_examples": [],
        "interaction_examples": [
            "copy-to-clipboard",
        ],
        "gaps": [
            {"text": "No payment page pattern. There's no example showing amount-due, payment method selector, payee/payor, terms, submit-and-receipt.",
             "cross_cutting_refs": ["payment"],
             "flavor_note": "Standalone payment surface for fines and fees."},
            {"text": "No dispute path pattern. Many fines have a 'pay or dispute' choice on the same surface.",
             "cross_cutting_refs": ["payment"],
             "flavor_note": "Pay-or-dispute branch on the payment surface; only applies to obligations that allow dispute."},
            {"text": "No receipt page pattern.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Payment-receipt flavor of submission-receipt: confirms payment with downloadable proof."},
            {"text": "No look-up-then-pay pattern. Many fines require finding your fine first.",
             "cross_cutting_refs": ["look-up-and-pick", "payment"],
             "flavor_note": "Two-step entry: find the obligation then pay; common when citizens don't have a reference number to hand."},
        ],
        "proposed_examples": [
            {"concept": "Lookup-and-pay",
             "rationale": "Two-step flow: find the obligation, then pay it.",
             "cross_cutting_refs": ["look-up-and-pick", "payment"],
             "flavor_note": "Citizen-facing lookup of their own obligation (by name, plate, file number) → pay."},
            {"concept": "Pay-or-dispute",
             "rationale": "Page that presents amount and a clear branch to dispute.",
             "cross_cutting_refs": ["payment"],
             "flavor_note": "Branching variant of payment: dispute opens a separate intake; pay completes the flow."},
            {"concept": "Payment receipt",
             "rationale": "Confirmation page with downloadable proof.",
             "cross_cutting_refs": ["results"],
             "flavor_note": "Payment-receipt flavor of submission-receipt."},
            {"concept": "Account-balance view",
             "rationale": "For multi-payment obligations (royalties, taxes), a balance-and-history page.",
             "cross_cutting_refs": ["my-account"],
             "flavor_note": "Balance-and-history view for citizens with recurring obligations; converges with the account/portal productType."},
        ],
        "note": "This service type likely earns its own productType in a future PR — payment is structurally distinct from public-form.",
    },
    {
        "id": "check-status-or-records",
        "name": "Check your status or records",
        "service_task": "Check",
        "kate_tarling_intents": ["checking-information"],
        "value_weight": "high",
        "value_weight_rationale": "Reach: every benefit recipient, every licence holder, every student loan borrower. Anchors the account/portal productType candidate.",
        "shared_shape": "Authenticated citizen looks up their own status, account, history, or records held by government. Often the back-half of an Apply or Transact flow.",
        "variations": "Status checks (immigration application, health coverage) vs. account management (student loan, support payments) vs. personal records (health records).",
        "product_types_used": [],
        "product_types_proposed": ["account", "portal"],
        "matcher": matches_check_status,
        "existing_examples": [],
        "interaction_examples": [
            "display-user-information",
            "show-status-on-a-card",
            "show-quick-links",
            "show-a-user-progress",
            "show-a-user-progress-when-the-time-is-unknown",
            "set-a-specific-tab-to-be-active",
            "show-multiple-tags-together",
            "show-full-date-in-a-tooltip",
        ],
        "gaps": [
            {"text": "No authenticated-account-home pattern.",
             "cross_cutting_refs": ["my-account"],
             "flavor_note": "Landing surface for the whole check-status type; the home itself."},
            {"text": "No history/timeline pattern.",
             "cross_cutting_refs": ["my-account"],
             "flavor_note": "Sub-pattern inside my-account: chronological list of past events with detail-view links."},
            {"text": "No status-with-action-affordance pattern. Often the status check leads to action (apply for deferral, dispute charge).",
             "cross_cutting_refs": ["status-tracking", "my-account"],
             "flavor_note": "'And now what?' affordances on a status surface inside the account home."},
            {"text": "No record-detail pattern.",
             "cross_cutting_refs": ["my-account"],
             "flavor_note": "Sub-pattern inside my-account: one record's full info with contextual actions."},
        ],
        "proposed_examples": [
            {"concept": "My-account home",
             "rationale": "Landing page with status cards, recent activity, and quick actions.",
             "cross_cutting_refs": ["my-account"]},
            {"concept": "History timeline",
             "rationale": "List of past events (payments, decisions, applications) with filters and detail-view links.",
             "cross_cutting_refs": ["my-account"],
             "flavor_note": "Timeline sub-pattern inside my-account."},
            {"concept": "Record detail with actions",
             "rationale": "Page showing one record's full info with contextual actions (renew, dispute, download).",
             "cross_cutting_refs": ["my-account"],
             "flavor_note": "Detail-view sub-pattern inside my-account."},
        ],
        "note": "Likely needs an account / portal productType beyond workspace and public-form. The proposed examples here anchor that productType.",
    },
    {
        "id": "search-a-public-register",
        "name": "Search a public register",
        "service_task": "Find",
        "kate_tarling_intents": ["checking-information"],
        "value_weight": "high",
        "value_weight_rationale": "Reach: high (land titles, court records used heavily by businesses, lawyers, citizens). Anchors the registry-search variation of the directory productType candidate.",
        "shared_shape": "Citizen queries a public registry to verify a fact, find a record, or check status. May be free (most) or paid (court records, land titles). Result is a record or 'no record found.'",
        "variations": "Validation queries (is this professional registered?) vs. record retrieval (land title, court record) vs. lookup-and-decide (is this drug covered? is broadband available?). Some require authenticated access.",
        "product_types_used": [],
        "product_types_proposed": ["directory"],
        "matcher": matches_search_register,
        "existing_examples": [
            {"productType": "(no productType)", "slug": "search"},
        ],
        "interaction_examples": [
            "card-grid",
            "show-status-in-a-table",
            "filter-data-in-a-table",
            "show-multiple-tags-together",
            "show-quick-links",
        ],
        "gaps": [
            {"text": "No verify-a-fact pattern. 'Is this professional registered?' is yes/no with details."},
            {"text": "No paid-search-with-payment pattern. Court records and land titles cost money.",
             "cross_cutting_refs": ["payment"],
             "flavor_note": "Pay-to-retrieve flavor: payment is gating record retrieval, not gating the whole flow."},
            {"text": "No record-citation pattern. Records often need to be cited (legal proceedings, applications)."},
        ],
        "proposed_examples": [
            {"concept": "Verification result",
             "rationale": "'We found one match; here's what they're authorized to do' — yes/no with detail."},
            {"concept": "Paid-record retrieval",
             "rationale": "Three-step pattern: search → confirm + pay → retrieve.",
             "cross_cutting_refs": ["payment"],
             "flavor_note": "Pay-to-retrieve flavor: payment between search confirmation and record release."},
            {"concept": "Citation-ready record view",
             "rationale": "Printable, downloadable, or share-link pattern."},
        ],
    },
    {
        "id": "find-a-service-or-place",
        "name": "Find a service or place",
        "service_task": "Find",
        "kate_tarling_intents": ["checking-information"],
        "value_weight": "high",
        "value_weight_rationale": "Reach: every citizen who needs help finding a service. Need: people often in crisis (doctors, victim services, mental health). Anchors the provider-directory variation of the directory productType candidate.",
        "shared_shape": "Citizen searches by location and need, gets a directory of providers/places with contact info, hours, eligibility hints. Often the front-half of an Advise or Apply flow.",
        "variations": "Health providers (doctors, treatment, hospitals) vs. social supports (settlement services, victim services, mental health) vs. physical places (libraries, parks, government offices) vs. regulated providers.",
        "product_types_used": [],
        "product_types_proposed": ["directory"],
        "matcher": matches_find_service_place,
        "existing_examples": [
            {"productType": "(no productType)", "slug": "search"},
        ],
        "interaction_examples": [
            "card-grid",
            "header-with-navigation",
            "hero-banner-with-actions",
            "show-a-list-to-help-answer-a-question",
            "show-multiple-tags-together",
            "show-quick-links",
            "link-to-an-external-page",
        ],
        "gaps": [
            {"text": "No location-based-search pattern. 'Near me' is common — no example handles geolocation or postal code with results map."},
            {"text": "No filter-by-criteria pattern for a directory."},
            {"text": "No directory-card-with-contact-info pattern with the standard facts."},
            {"text": "No no-results-with-recovery pattern."},
        ],
        "proposed_examples": [
            {"concept": "Directory search page",
             "rationale": "Combined filters + results in a public-facing directory shape. Anchors the `directory` productType candidate (provider-directory variation)."},
            {"concept": "Provider/place card",
             "rationale": "Standard result card with name, location, hours, contact, eligibility, accessibility."},
            {"concept": "Empty state with recovery",
             "rationale": "No-results pattern that suggests broader searches or contact."},
            {"concept": "Result detail page",
             "rationale": "Click-through view of one provider with full info."},
        ],
    },
    {
        "id": "access-an-in-person-program",
        "name": "Access an in-person program",
        "service_task": "Advise",
        "kate_tarling_intents": ["financial-support", "protecting"],
        "value_weight": "low",
        "value_weight_rationale": "No digital surface to design for. The gap is digitization, not design system. Value-weighting can't change that for this analysis.",
        "intent_note": "Multi-intent. Emergency $ supports lean financial-support; shelter/crisis services lean protecting.",
        "shared_shape": "Service exists but has no digital channel — citizen finds the program, calls or visits in person, gets human-mediated intake, receives the service. The digital surface (if any) is find-a-service-or-place shaped pointing at the program.",
        "variations": "Emergency/crisis services (shelter, evacuation support, crisis lines) vs. specialized in-person supports (food bank, addiction treatment, brain injury). Concentrated in ALSS/SCSS plus MHA, JUS, CFS.",
        "product_types_used": [],
        "matcher": matches_access_in_person,
        "existing_examples": [],
        "interaction_examples": [],
        "gaps": [
            {"text": "By definition this is the gap. ~11% of Alberta services have no digital channel."},
        ],
        "proposed_examples": [],
        "note": "No new examples in this brief. Brief 07 should surface this category as 'services without a digital surface; design system can't help build for these until digitization decision is made.' The forward-looking response is intake-and-assess productType pairs (worker side), pursued in a follow-up brief per scope.",
    },
    {
        "id": "read-information-or-guidance",
        "name": "Read information or guidance",
        "service_task": "Find",
        "kate_tarling_intents": ["checking-information"],
        "value_weight": "low",
        "value_weight_rationale": "Content not action. Design system action surface doesn't differentiate this category regardless of value-weighting.",
        "shared_shape": "Citizen consumes content explaining a topic, regulation, right, or program. No personalization; published guidance for general audiences. Often the only digital surface for non-digitized programs.",
        "variations": "Rights/regulation content vs. program awareness vs. data and statistics vs. how-to guides. Quality and depth vary.",
        "product_types_used": [],
        "matcher": matches_read_information,
        "existing_examples": [
            {"productType": "(no productType)", "slug": "basic-page-layout"},
            {"productType": "(no productType)", "slug": "hero-banner-with-actions"},
        ],
        "interaction_examples": [
            "show-links-to-navigation-items",
            "show-quick-links",
            "link-to-an-external-page",
            "hide-and-show-many-sections-of-information",
            "show-a-section-title-on-a-question-page",
        ],
        "gaps": [
            {"text": "No structured-guidance page pattern."},
            {"text": "No 'rules and rights' pattern."},
            {"text": "No content-with-tools pattern (calculators, eligibility checkers embedded in guidance)."},
        ],
        "proposed_examples": [
            {"concept": "Long-form guidance page",
             "rationale": "Standard structure for explanatory content."},
            {"concept": "Rules-and-rights page",
             "rationale": "Specific pattern for rights/obligations content."},
            {"concept": "Inline calculator",
             "rationale": "Mini-tool embedded in guidance."},
        ],
        "note": "This service type is the largest in the corpus but has the lowest design-system value because it's content rather than action. Brief 07 should surface it as 'this category exists; the design system is action-shaped and does not yet differentiate offerings here.'",
    },
]


def assign_types(services):
    """Assign each service to the first matching service type. Returns
    (assignments dict mapping type_id → list of services, uncategorised list)."""
    assignments = defaultdict(list)
    uncategorised = []
    for s in services:
        # Skip services where the primary task isn't action-bearing for any type
        # (No-channels, Unclassified) — they go straight to uncategorised
        if s["primary_task"] in ("No-channels", "Unclassified"):
            uncategorised.append(s)
            continue
        matched = False
        for st in SERVICE_TYPES:
            if st["matcher"](s):
                assignments[st["id"]].append(s)
                matched = True
                break
        if not matched:
            uncategorised.append(s)
    return assignments, uncategorised


# Priority bucketing (Brief 08, Phase 3). Mechanical signal (leverage) plus
# value-weighting (curated per type and per cross-cutting). When value_weight is set
# on a type or cross-cutting entry, it overrides the mechanical default and the
# rationale captures both reasons.

RANK = {"high": 3, "medium": 2, "low": 1}


def _reach_bucket(applies_to_count):
    """Convert cross-cutting reach (number of types affected) into a priority bucket."""
    if applies_to_count >= 4:
        return "high"
    if applies_to_count == 3:
        return "medium"
    return "low"


def _weight_bucket(service_count):
    """Convert service-type weight (number of services) into a priority bucket."""
    if service_count >= 50:
        return "high"
    if service_count >= 20:
        return "medium"
    return "low"


def compute_priority(entry, type_id, type_leverage, cross_cutting_index, type_index):
    """Compute priority for a gap or proposed_example.

    Two layered inputs:
    - Mechanical signal: service-count bucket (per-type) OR cross-cutting reach bucket.
    - Value-weighting: per-type or per-cross-cutting curated value_weight that captures
      reach (citizen volume), financial flow, need / hurt, and dependency / levers.

    When value_weight is set, it overrides the mechanical default. The rationale
    surfaces both signals so the override is visible.

    Returns (priority, priority_rationale).
    """
    refs = entry.get("cross_cutting_refs", [])

    # Cross-cutting-referencing entries follow the strongest cross-cutting ref's priority.
    if refs:
        best_priority = None
        best_ref_id = None
        best_rationale = None
        for ref_id in refs:
            cc = cross_cutting_index.get(ref_id)
            if not cc:
                continue
            n = len(cc["applies_to"])
            mechanical = _reach_bucket(n)
            value_weight = cc.get("value_weight")
            value_weight_rationale = cc.get("value_weight_rationale", "")

            if value_weight:
                this_priority = value_weight
                this_rationale = (
                    f"Cross-cutting ({ref_id}) reach: {n} types (mechanical: {mechanical}). "
                    f"Value-weighting: {value_weight} — {value_weight_rationale}"
                )
            else:
                this_priority = mechanical
                this_rationale = f"Cross-cutting gap ({ref_id}) affects {n} types."

            if best_priority is None or RANK[this_priority] > RANK[best_priority]:
                best_priority = this_priority
                best_ref_id = ref_id
                best_rationale = this_rationale

        if best_priority is not None:
            return best_priority, best_rationale

    # Per-type entry — use type's value_weight (override) or mechanical leverage.
    s = type_leverage["service_count"]
    m = type_leverage["ministry_count"]
    mechanical = _weight_bucket(s)

    type_def = type_index.get(type_id, {})
    value_weight = type_def.get("value_weight")
    value_weight_rationale = type_def.get("value_weight_rationale", "")

    if value_weight:
        rationale = (
            f"Service-type weight: {s} services across {m} ministries (mechanical: {mechanical}). "
            f"Value-weighting: {value_weight} — {value_weight_rationale}"
        )
        return value_weight, rationale

    return mechanical, f"Service-type weight: {s} services across {m} ministries."


def annotate_with_priority(entries, type_id, type_leverage, cross_cutting_index, type_index):
    """Walk a list of gaps or proposed_examples, attach priority + priority_rationale to each."""
    out = []
    for entry in entries:
        priority, rationale = compute_priority(entry, type_id, type_leverage, cross_cutting_index, type_index)
        annotated = dict(entry)
        annotated["priority"] = priority
        annotated["priority_rationale"] = rationale
        out.append(annotated)
    return out


def build_artifact(assignments, args):
    # Cross-cutting gaps: patterns that recur across multiple service types and are
    # missing from the design system. Each entry has `applies_to` (the service types
    # that share this gap), and optionally `variants` (for results, which is a parent
    # pattern with five shape variations) or `flavors` (for status-tracking, which
    # is one structural pattern with per-type content variations).
    cross_cutting_gaps = [
        {
            "id": "eligibility-checking",
            "name": "Eligibility checking before applying",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "apply-for-a-grant-or-funding"],
            "summary": "Citizens need to know if they qualify before starting an application. No canonical pattern. Sometimes 4-5 questions yielding yes/no/maybe with reasons; sometimes an embedded calculator in guidance content.",
            "value_weight": "high",
            "value_weight_rationale": "Reach: everyone who considers applying asks this first. High frustration relief.",
        },
        {
            "id": "status-tracking",
            "name": "Status tracking after submission",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "apply-for-a-grant-or-funding", "report-a-concern-or-incident", "file-a-complaint", "appeal-a-decision", "request-government-action-or-records", "check-status-or-records"],
            "summary": "One structural pattern (where is my thing in its journey, what's expected, what can I act on) with per-type content flavors. result-page covers the immediate confirmation, not the long wait. Must include 'and now what?' affordances when the citizen can act (apply for deferral, dispute, withdraw).",
            "value_weight": "high",
            "value_weight_rationale": "Reach: every applicant. Spans benefits, licences, grants, appeals, complaints, records requests. High frustration relief on long waits.",
            "flavors": [
                {"service_type": "apply-for-a-benefit", "note": "Long-running decision tracking with clarification-request branch."},
                {"service_type": "apply-for-a-licence-or-permit", "note": "Application status + renewal-reminder timing."},
                {"service_type": "apply-for-a-grant-or-funding", "note": "Multi-phase tracking: submission → review → award → reporting."},
                {"service_type": "report-a-concern-or-incident", "note": "Reference number lookup; investigation may not loop back to reporter."},
                {"service_type": "file-a-complaint", "note": "Long-running investigation status surfacing; months not days."},
                {"service_type": "appeal-a-decision", "note": "Distinct appeal milestones; three-branch outcome ahead."},
                {"service_type": "request-government-action-or-records", "note": "Legislated timeline surfaced (FOI 30 days)."},
                {"service_type": "check-status-or-records", "note": "This whole service type is the status surface; primarily the 'and now what?' affordance side."},
            ],
        },
        {
            "id": "save-and-return",
            "name": "Save and return across sessions",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-grant-or-funding", "apply-for-a-licence-or-permit"],
            "summary": "Long applications can't be done in one sitting; the public-form template assumes one session. Couples with my-account for the partial-fill state landing.",
            "value_weight": "high",
            "value_weight_rationale": "Reach: anyone filling a long form. Means-tested benefit applications run 30-60 minutes; many citizens can't finish in one sitting.",
        },
        {
            "id": "my-account",
            "name": "My account home",
            "applies_to": ["check-status-or-records", "apply-for-a-licence-or-permit", "appeal-a-decision", "apply-for-a-benefit", "pay-a-fee-or-fine"],
            "summary": "Authenticated home where citizens see their stuff (applications, status, history, records) and act on it (renew, dispute, download). Distinct as a pattern from the `account/portal` productType candidate, though the two converge in commitment.",
            "value_weight": "high",
            "value_weight_rationale": "Reach: every authenticated citizen. Anchors the account/portal productType candidate.",
        },
        {
            "id": "payment",
            "name": "Payment",
            "applies_to": ["apply-for-a-licence-or-permit", "search-a-public-register", "pay-a-fee-or-fine"],
            "summary": "Pay an amount as part of a service interaction. Couples with licence applications and renewals, paid registry searches, fees and fines. Distinct as a pattern from the `payment` productType candidate (which would be the whole pay-a-fee surface).",
            "value_weight": "high",
            "value_weight_rationale": "Financial: billions/year. Includes traffic fines, fuel tax, paid registry searches, licence application fees.",
        },
        {
            "id": "service-messages",
            "name": "Messages from government",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "report-a-concern-or-incident", "file-a-complaint", "apply-for-a-grant-or-funding"],
            "summary": "Emails, texts, in-app messages government sends citizens when state changes (we received it, we need more info, your decision is ready, your licence expires in 30 days). No template exists for how these are structured (subject, body, call-to-action, link to landing page).",
            "value_weight": "high",
            "value_weight_rationale": "Reach: every applicant receives at least one. Decision letters, renewal reminders, clarification requests, status updates.",
        },
        {
            "id": "results",
            "name": "Results",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "apply-for-a-grant-or-funding", "file-a-complaint", "appeal-a-decision", "request-government-action-or-records", "register-something", "report-a-concern-or-incident", "pay-a-fee-or-fine"],
            "summary": "One parent pattern (what happened, what's next, contact path) with content variants based on what the result is. The current `result-page` is the only candidate in the design system and is thin for the breadth of cases.",
            "value_weight": "high",
            "value_weight_rationale": "Reach: every service interaction ends in a result page of some kind. Five content variants cover decision letters, credentials, records release, appeal outcomes, submission receipts.",
            "variants": [
                {"id": "submission-receipt", "name": "Submission receipt", "summary": "We received your thing; here's your reference number. Sent immediately at submission. Light content."},
                {"id": "decision-letter", "name": "Decision letter", "summary": "Outcome of an application with reasoning and next steps. Long-form."},
                {"id": "issued-credential", "name": "Issued credential", "summary": "Outcome plus a granted thing (licence, certificate). Print/save/wallet-add affordances."},
                {"id": "records-release", "name": "Records release", "summary": "Outcome IS the records themselves, often with redaction explanation."},
                {"id": "appeal-outcome", "name": "Appeal outcome", "summary": "Three-branch decision (uphold / overturn / remit) with reasoning."},
            ],
        },
        {
            "id": "submit-supporting-documents",
            "name": "Submit supporting documents",
            "applies_to": ["apply-for-a-grant-or-funding", "report-a-concern-or-incident", "file-a-complaint", "request-government-action-or-records", "apply-for-a-benefit", "apply-for-a-licence-or-permit"],
            "summary": "Multi-document checklist with upload status. 'Here are the N documents we need; here's which you've uploaded; here's what's missing.' Distinct from a single file-upload field.",
            "value_weight": "high",
            "value_weight_rationale": "Reach: high. Common in grant applications, reports, complaints, records requests, benefit applications, licence applications. High friction point when not handled well.",
        },
        {
            "id": "describe-what-happened",
            "name": "Describe what happened, in order",
            "applies_to": ["file-a-complaint", "appeal-a-decision", "report-a-concern-or-incident"],
            "summary": "Structured event-sequence input where the citizen recounts a sequence of events. Date-tagged segments, event-by-event, ordered. Distinct from a free-text textarea.",
            "value_weight": "medium",
            "value_weight_rationale": "Bounded volume (complaints, appeals, reports). Important for accuracy but not high-reach.",
        },
        {
            "id": "look-up-and-pick",
            "name": "Look up and pick (inside a flow)",
            "applies_to": ["file-a-complaint", "apply-for-a-licence-or-permit", "report-a-concern-or-incident", "appeal-a-decision"],
            "summary": "Embedded entity lookup as a step inside another flow: find the doctor you're complaining about, look up your existing licence to renew, identify the regulated party. Distinct from the `directory` productType which is the whole shape.",
            "value_weight": "high",
            "value_weight_rationale": "Sub-pattern but widely embedded. Useful in complaints, renewals, reports, find-place flows.",
        },
    ]

    excluded_or_below_bar = [
        {
            "id": "engage-in-consultation",
            "reason": "Below leverage bar (4 services, 3 ministries). Worth re-checking when more consultation services are added or another jurisdiction included.",
        },
        {
            "id": "buy-or-acquire-rights",
            "reason": "7 services concentrated in EM (energy_minerals); below ministry-spread bar of 3+ ministries with meaningful counts. Alberta-specific industrial pattern, not a general design system service type.",
        },
        {
            "id": "schedule-or-book-something",
            "reason": "Borderline; only 4-6 candidate services across ~3 ministries (campsite reservation, road test, transportation booking). Below leverage bar. Watch for growth.",
        },
    ]

    # Build indexes for compute_priority lookups.
    cross_cutting_index = {cc["id"]: cc for cc in cross_cutting_gaps}
    type_index = {st["id"]: st for st in SERVICE_TYPES}

    # Annotate each cross-cutting entry with its own priority. Use value_weight when
    # set; otherwise fall back to mechanical reach.
    for cc in cross_cutting_gaps:
        n = len(cc["applies_to"])
        mechanical = _reach_bucket(n)
        value_weight = cc.get("value_weight")
        if value_weight:
            cc["priority"] = value_weight
            cc["priority_rationale"] = (
                f"Cross-cutting reach: {n} types (mechanical: {mechanical}). "
                f"Value-weighting: {value_weight} — {cc.get('value_weight_rationale', '')}"
            )
        else:
            cc["priority"] = mechanical
            cc["priority_rationale"] = f"Cross-cutting reach: affects {n} service types."

    # Also annotate each service type with a top-level priority based on its
    # value_weight (and fallback mechanical). This makes the type's overall standing
    # visible in addition to per-entry priorities.
    service_types_out = []
    for st in SERVICE_TYPES:
        members = assignments.get(st["id"], [])
        ministries = sorted({m["ministry_prefix"] for m in members})
        passes = len(members) >= 5 and len(ministries) >= 3

        services_field = [
            {
                "ministry": m["ministry_prefix"],
                "name": m["name"],
                "domain": m.get("domain"),
                "track": m.get("track"),
                "tier": m.get("tier"),
            }
            for m in sorted(members, key=lambda x: (x["ministry_prefix"], x["name"]))
        ]

        leverage = {
            "service_count": len(members),
            "ministry_count": len(ministries),
            "passes_bar": passes,
        }

        # Type-level priority: value_weight (if set) overrides mechanical service-count bucket.
        mechanical = _weight_bucket(len(members))
        value_weight = st.get("value_weight")
        if value_weight:
            type_priority = value_weight
            type_priority_rationale = (
                f"Service-type weight: {len(members)} services across {len(ministries)} ministries (mechanical: {mechanical}). "
                f"Value-weighting: {value_weight} — {st.get('value_weight_rationale', '')}"
            )
        else:
            type_priority = mechanical
            type_priority_rationale = f"Service-type weight: {len(members)} services across {len(ministries)} ministries."

        gaps_annotated = annotate_with_priority(
            st.get("gaps", []), st["id"], leverage, cross_cutting_index, type_index
        )
        proposed_annotated = annotate_with_priority(
            st.get("proposed_examples", []), st["id"], leverage, cross_cutting_index, type_index
        )

        entry = {
            "id": st["id"],
            "name": st["name"],
            "service_task": st["service_task"],
            "kate_tarling_intents": st["kate_tarling_intents"],
            "leverage": leverage,
            "priority": type_priority,
            "priority_rationale": type_priority_rationale,
            "shared_shape": st["shared_shape"],
            "variations": st["variations"],
            "product_types_used": st.get("product_types_used", []),
            "existing_examples": st.get("existing_examples", []),
            "interaction_examples": st.get("interaction_examples", []),
            "gaps": gaps_annotated,
            "proposed_examples": proposed_annotated,
            "services": services_field,
        }
        if "value_weight" in st:
            entry["value_weight"] = st["value_weight"]
            entry["value_weight_rationale"] = st.get("value_weight_rationale", "")
        if "intent_note" in st:
            entry["intent_note"] = st["intent_note"]
        if "extension_note" in st:
            entry["is_extension"] = True
            entry["extension_note"] = st["extension_note"]
        if "product_types_proposed" in st:
            entry["product_types_proposed"] = st["product_types_proposed"]
        if "note" in st:
            entry["note"] = st["note"]

        service_types_out.append(entry)

    artifact = {
        "$schema_version": "0.3",
        "jurisdiction": "ab",
        "generated": date.today().isoformat(),
        "purpose": "Service-type analysis of Alberta ministry maps. Each type is a (service task × Kate Tarling intent) cluster validated by the leverage bar (5+ services across 3+ ministries). Per-gap and per-proposed-example priority signals applied, layered from mechanical leverage and curated value-weighting (reach, financial value, need, dependency).",
        "service_tasks": SERVICE_TASKS,
        "kate_tarling_intents": KATE_TARLING_INTENTS,
        "service_types": service_types_out,
        "cross_cutting_gaps": cross_cutting_gaps,
        "excluded_or_below_bar": excluded_or_below_bar,
        "source": {
            "data_dir": "data/ab/",
            "method": "phase-1-classification of 637 supporting services by primary service task (channel-based with name-pattern overrides), then phase-2 clustering by name pattern within each task with leverage bar applied. A critical-pass dedup followed: per-type gaps and proposed_examples that duplicate cross-cutting patterns now carry cross_cutting_refs and flavor_note fields. Priority is computed from two layered signals — mechanical (service-type weight or cross-cutting reach) and value-weighting (curated per type and per cross-cutting using reach, financial flow, need, dependency). When value_weight is set, it overrides the mechanical default and the rationale surfaces both reasons.",
            "constraints_applied": [
                "Citizen-side only. Worker-side service types (intake-and-assess, case management) deferred to a follow-up brief.",
                "Product demo patterns NOT used as input to avoid biasing the system view.",
                "Size-agnostic example proposals — captures the concept rather than the size class.",
                "Value-weighting is a first-pass curation (Tom 2026-05-19, with input from Paul). Refinable as data sources for citizen reach and financial flow become available.",
                "ALSS pilot tie-in not applied — pilot service pick happening over the next two weeks; matching service type's priority_rationale gets a targeted amendment once known.",
            ],
        },
    }

    return artifact, service_types_out


def generate_summary(artifact):
    """Generate a human-readable service_types.md from the artifact dict.

    Sorted by priority (high → low) for both service types and cross-cutting patterns.
    Auto-generated; do not hand-edit.
    """
    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    lines = []
    lines.append("<!--")
    lines.append("AUTO-GENERATED. Do not edit by hand.")
    lines.append("Regenerate with: cd analysis/service-types && python3 build_service_types.py")
    lines.append("Edit the build script (or its inputs), not this file.")
    lines.append("-->")
    lines.append("")
    lines.append("# Alberta service types")
    lines.append("")
    lines.append(f"Generated {artifact['generated']} from the ministry maps in this repo. The structured data lives next to this file in `service_types.json`; this doc is the readable summary.")
    lines.append("")

    lines.append("## What this is")
    lines.append("")
    lines.append("For any given service in Alberta, this analysis answers: what kind of service is it in the design-system / shape sense? Which other services across ministries share its shape? Which patterns and components down the design-system stack are reachable from it?")
    lines.append("")
    lines.append("A **service type** is a `(service task × Kate Tarling intent)` cluster validated by a leverage bar (5+ services across 3+ ministries). It's the most stable thing about a service — channels and legislation change, the type rarely does.")
    lines.append("")

    lines.append("## How priority is computed")
    lines.append("")
    lines.append("Each service type, gap, and proposed example carries a `priority` field (high / medium / low) layered from two signals:")
    lines.append("")
    lines.append("- **Mechanical leverage** — service-type weight (services in the type) or cross-cutting reach (types sharing this gap). Defensible from data alone.")
    lines.append("- **Value-weighting** — curated using four dimensions: reach (citizens), financial flow, need / hurt, dependency / levers.")
    lines.append("")
    lines.append("When value-weighting is set, it overrides the mechanical default. The `priority_rationale` field surfaces both reasons so the override is visible.")
    lines.append("")

    lines.append("## Service tasks")
    lines.append("")
    lines.append("Seven shapes describing how the citizen interacts:")
    lines.append("")
    lines.append("| Task | What the citizen does |")
    lines.append("|---|---|")
    lines.append("| **Apply** | Demonstrates eligibility, submits, waits for a decision |")
    lines.append("| **Transact** | Pays, renews, files, buys — completes a routine exchange |")
    lines.append("| **Check** | Looks up status, records, history (authenticated to themselves) |")
    lines.append("| **Report** | Pushes information about a hazard or third party |")
    lines.append("| **Engage** | Participates in a consultation or decision process |")
    lines.append("| **Find** | Looks up information, services, or providers |")
    lines.append("| **Advise** | Gets human-mediated help; no digital action surface today |")
    lines.append("")

    # Priority-grouped service types
    lines.append("## The service types, sorted by priority")
    lines.append("")
    types_by_priority = {"high": [], "medium": [], "low": []}
    for st in artifact["service_types"]:
        types_by_priority[st["priority"]].append(st)
    for bucket in types_by_priority:
        types_by_priority[bucket].sort(key=lambda x: -x["leverage"]["service_count"])

    for priority_label in ["high", "medium", "low"]:
        bucket = types_by_priority[priority_label]
        if not bucket:
            continue
        lines.append(f"### {priority_label.title()} priority ({len(bucket)})")
        lines.append("")
        lines.append("| ID | Task | Members | Shape | Value-weight reasoning |")
        lines.append("|---|---|---|---|---|")
        for st in bucket:
            shape_short = st["shared_shape"].split(".")[0] + "."
            vw_rationale = st.get("value_weight_rationale", "")
            # Trim long rationales
            if len(vw_rationale) > 180:
                vw_rationale = vw_rationale[:177] + "..."
            members = f"{st['leverage']['service_count']} svc / {st['leverage']['ministry_count']} min"
            lines.append(f"| `{st['id']}` | {st['service_task']} | {members} | {shape_short} | {vw_rationale} |")
        lines.append("")

    # Cross-cutting patterns
    lines.append("## Cross-cutting patterns, sorted by priority")
    lines.append("")
    lines.append("Patterns that recur across multiple service types. Each per-type gap or proposed example that maps to one of these carries a `cross_cutting_refs` pointer in the JSON.")
    lines.append("")
    cc_by_priority = {"high": [], "medium": [], "low": []}
    for cc in artifact["cross_cutting_gaps"]:
        cc_by_priority[cc["priority"]].append(cc)
    for bucket in cc_by_priority:
        cc_by_priority[bucket].sort(key=lambda x: -len(x["applies_to"]))

    for priority_label in ["high", "medium", "low"]:
        bucket = cc_by_priority[priority_label]
        if not bucket:
            continue
        lines.append(f"### {priority_label.title()} priority ({len(bucket)})")
        lines.append("")
        lines.append("| ID | Applies to | Summary | Value-weight reasoning |")
        lines.append("|---|---|---|---|")
        for cc in bucket:
            applies_count = len(cc["applies_to"])
            summary_short = cc["summary"].split(".")[0] + "."
            vw_rationale = cc.get("value_weight_rationale", "")
            if len(vw_rationale) > 180:
                vw_rationale = vw_rationale[:177] + "..."
            lines.append(f"| `{cc['id']}` | {applies_count} types | {summary_short} | {vw_rationale} |")
        lines.append("")

    # Coverage
    total_services = sum(st["leverage"]["service_count"] for st in artifact["service_types"])
    lines.append("## Coverage")
    lines.append("")
    lines.append(f"- **{total_services} services** classified into {len(artifact['service_types'])} service types across 28 Alberta ministries.")
    lines.append("- ~38 uncategorised edge cases — concentrated in JUS-only legal protection orders, EM-only industrial buying, scheduling-shape services, niche disputes. All below the leverage bar.")
    lines.append("")

    # Methodology
    lines.append("## Methodology")
    lines.append("")
    lines.append(artifact["source"]["method"])
    lines.append("")
    lines.append("**Constraints:**")
    lines.append("")
    for c in artifact["source"]["constraints_applied"]:
        lines.append(f"- {c}")
    lines.append("")

    # Files
    lines.append("## Files")
    lines.append("")
    lines.append("- `service_types.json` — full structured analysis (the source of truth, including per-type gaps, proposed examples, services, and priority rationales).")
    lines.append("- `service_types.md` — this document (auto-generated from the JSON).")
    lines.append("- `analysis/service-types/` — build pipeline scripts and working notes.")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry", action="store_true", help="print summary without writing")
    args = parser.parse_args()

    data = json.loads(CLASSIFICATION.read_text())
    services = data["services"]

    assignments, uncategorised = assign_types(services)
    artifact, service_types_out = build_artifact(assignments, args)

    print(f"Service types: {len(service_types_out)}")
    print()
    for st in service_types_out:
        passes = "✓" if st["leverage"]["passes_bar"] else "✗"
        print(f"  {passes} {st['id']:<35s}  {st['leverage']['service_count']:3d} svc / {st['leverage']['ministry_count']:2d} min")
    print()
    print(f"Uncategorised: {len(uncategorised)} services")
    if uncategorised:
        print("  (see phase-4-uncategorised.txt for full list)")

    UNCATEGORISED.write_text(
        "\n".join(
            f"[{s['ministry_prefix']:8s}] [{s['primary_task']:14s}] {s['name']}"
            for s in sorted(uncategorised, key=lambda x: (x["primary_task"], x["ministry_prefix"], x["name"]))
        )
    )

    if args.dry:
        print()
        print("--dry: skipping write")
        return

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as fp:
        json.dump(artifact, fp, indent=2, ensure_ascii=False)
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print()
    print(f"Wrote {OUTPUT_PATH} ({size_kb:.1f} KB)")

    # Also generate the human-readable summary (auto-synced with the JSON).
    summary_path = OUTPUT_PATH.with_suffix(".md")
    summary_path.write_text(generate_summary(artifact))
    summary_kb = summary_path.stat().st_size / 1024
    print(f"Wrote {summary_path} ({summary_kb:.1f} KB)")


if __name__ == "__main__":
    main()
