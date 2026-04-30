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
            "No reference-the-original-decision pattern. Appeals start with a specific prior decision and need to link/summarise it.",
            "No grounds-for-appeal composer. Appeals need structured reason categories (procedural, factual, new evidence).",
            "No appeal-status-tracking pattern.",
            "No appeal-outcome-with-action pattern (uphold/overturn/remit branches).",
        ],
        "proposed_examples": [
            {"concept": "Appeal initiation", "rationale": "Loads the original decision, lets the appellant select grounds and write reasoning."},
            {"concept": "Appeal status", "rationale": "Status tracker variant for appeals; differs from application status because the next steps and timelines are different."},
            {"concept": "Appeal outcome letter", "rationale": "Decision letter pattern with the three possible branches."},
        ],
    },
    {
        "id": "request-government-action-or-records",
        "name": "Request government records or action",
        "service_task": "Apply",  # Most are Apply-task; some are Find/Transact/Advise. Multi-task in reality.
        "kate_tarling_intents": ["checking-information", "protecting"],
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
            "No request-form pattern with required-info checklist (most have specific data needs).",
            "No status-of-request pattern. Many requests have legislated timelines (FOI is 30 days). Citizens need to track.",
            "No release-of-records pattern. After approval, the citizen receives the records — what does that page look like?",
        ],
        "proposed_examples": [
            {"concept": "Records request form", "rationale": "Form with required information checklist plus optional fields, fee handling, and consent."},
            {"concept": "Request status with timeline", "rationale": "Status page that surfaces the legislated timeline (e.g. FOI 30 days) and current step."},
            {"concept": "Released records view", "rationale": "Page or download experience for the released records, with redaction explanation if applicable."},
        ],
    },
    {
        "id": "file-a-complaint",
        "name": "File a complaint",
        "service_task": "Report",
        "kate_tarling_intents": ["protecting"],
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
            "No 'describe what happened' pattern with timeline support. Complaints often need a sequence of events.",
            "No regulated-party-search pattern. The citizen is filing against a regulated party — they need to find/identify that party.",
            "No status-update notification pattern. Investigations take months.",
            "No outcome-letter pattern (current result-page is too thin for complaint outcomes).",
            "No appeal-pathway pattern (overlaps with appeal-a-decision).",
        ],
        "proposed_examples": [
            {"concept": "Identify the regulated party", "rationale": "Search-and-select for finding the doctor / business / officer the complaint is about."},
            {"concept": "Timeline-of-events composer", "rationale": "Section pattern for ordered narrative input."},
            {"concept": "Investigation status updates", "rationale": "Long-running status surfacing; overlaps with check-status-or-records."},
            {"concept": "Decision letter view", "rationale": "Long-form decision page with reasoning, next steps, and appeal info."},
        ],
    },
    {
        "id": "report-a-concern-or-incident",
        "name": "Report a concern or incident",
        "service_task": "Report",
        "kate_tarling_intents": ["protecting"],
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
            "No anonymous-reporting affordance. Many reports allow or require anonymity.",
            "No report-receipt-with-reference-number pattern. Reporters need a way to follow up.",
            "No file-evidence-with-context pattern.",
            "No urgency-routing pattern. Some reports are time-critical (animal disease, wildfire).",
        ],
        "proposed_examples": [
            {"concept": "Optional-identity report form", "rationale": "Pattern showing the anonymous/named branch with consequence framing."},
            {"concept": "Report receipt with reference number", "rationale": "Page showing reference number, what happens next, contact path."},
            {"concept": "Evidence-attached-to-fact composer", "rationale": "Section pattern for uploading evidence linked to specific report items."},
        ],
    },
    {
        "id": "register-something",
        "name": "Register something",
        "service_task": "Apply",
        "kate_tarling_intents": ["registering-information", "becoming"],
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
            "No short-form (multi-fields-per-page) registration pattern. Public-form is one-question-per-page which is overkill for short registrations.",
            "No registry-confirmation receipt pattern. Result-page is decision-shaped (approved/denied); registrations should show the registry entry that was created.",
            "No update-existing-registration pattern. Registries are alive — change of address, name change after marriage.",
        ],
        "proposed_examples": [
            {"concept": "Compact form page", "rationale": "Multi-field registration form (12-20 fields) on one or two pages, denser than public-form per-idea pattern."},
            {"concept": "Registry receipt", "rationale": "Page showing the created record with ID, key facts, downloadable PDF, follow-on actions."},
            {"concept": "Update an existing record", "rationale": "Look-up → modify → confirm → updated-record-receipt flow."},
        ],
    },
    {
        "id": "apply-for-a-licence-or-permit",
        "name": "Apply for a licence or permit",
        "service_task": "Apply",
        "kate_tarling_intents": ["permission", "becoming"],
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
            "No declaration/attestation pattern. Most licences require the citizen to declare facts under penalty.",
            "No fitness-or-qualifications composer. Permits often require proof of training, experience hours, supervisor sign-off.",
            "No fee-with-application pattern. Many licences require payment at submission.",
            "No outcome-with-credential view. result-page exists but no example of 'here's your decision and your printable/wallet credential.'",
            "**Renewal-specific:** No look-up-existing pattern. Renewal starts with verifying who you are and pulling up your existing record.",
            "**Renewal-specific:** No diff-from-current pattern. Renewal usually shows 'here's what we have on file; change anything?'",
            "**Renewal-specific:** No renewal-reminder/notification pattern.",
        ],
        "proposed_examples": [
            {"concept": "Attestation / declaration", "rationale": "Section pattern with explicit affirmation, plain-language consequences, signature."},
            {"concept": "Qualifications composer", "rationale": "Section for showing training, hours, or external evidence."},
            {"concept": "Pay-and-submit", "rationale": "Coupled flow joining form review → payment → submission."},
            {"concept": "Issued credential page", "rationale": "Page showing decision and credential with print/save/wallet-add affordances."},
            {"concept": "Verify-and-renew flow", "rationale": "Renewal sub-shape: authenticate → see current record → confirm or edit → pay → updated credential."},
            {"concept": "Renewal reminder", "rationale": "Email/notification template + landing page for the renewal start."},
        ],
    },
    {
        "id": "apply-for-a-grant-or-funding",
        "name": "Apply for a grant or funding",
        "service_task": "Apply",
        "kate_tarling_intents": ["financial-support"],
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
            "No project-budget input pattern. Grant applications need structured cost tables.",
            "No multi-applicant/team pattern. Grants often need lists of project participants.",
            "No work-plan/milestone composer.",
            "No attachment manager. Grant applications often require multiple supporting documents.",
            "No reporting-back flow (post-award), though that's worker-side and deferred.",
        ],
        "proposed_examples": [
            {"concept": "Budget table input", "rationale": "Section composer with itemized rows, categories, totals."},
            {"concept": "Project team composer", "rationale": "Pattern for adding multiple participants with their own form fields each."},
            {"concept": "Document checklist with upload", "rationale": "Pattern showing required attachments with status indicators."},
            {"concept": "Multi-organization profile", "rationale": "Section for the org submitting (their address, registration, history)."},
        ],
    },
    {
        "id": "apply-for-a-benefit",
        "name": "Apply for a benefit",
        "service_task": "Apply",
        "kate_tarling_intents": ["financial-support"],
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
            "No eligibility-check pattern. Citizens often need to know if they qualify before starting.",
            "No means-test screen. Most Alberta benefits are means-tested; no example shows how to handle income+household+deductions in a form.",
            "No status-tracking page. The current result-page covers the immediate confirmation; nothing covers checking on a long-running decision.",
            "No clarification-request flow. When the worker side asks for more info.",
            "No save-and-return pattern. Means-tested applications are long; many citizens can't finish in one sitting.",
        ],
        "proposed_examples": [
            {"concept": "Eligibility checker", "rationale": "Pre-form gate: answer 4-5 questions, get a yes/no/maybe with reasons."},
            {"concept": "Status tracker", "rationale": "Page citizens visit after submitting to see where their application is. Phase 5 of Apply six-phase flow has no existing example."},
            {"concept": "Means-test composer", "rationale": "Section that handles eligibility math (income, household, deductions) with explanatory help."},
            {"concept": "Save-and-return", "rationale": "Pattern for partial-fill state across sessions plus account-side pages."},
            {"concept": "Respond to a clarification request", "rationale": "Page or flow citizen reaches via notification, lets them upload more info or answer follow-ups."},
        ],
    },
    {
        "id": "pay-a-fee-or-fine",
        "name": "Pay a fee or fine",
        "service_task": "Transact",
        "kate_tarling_intents": ["paying"],
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
            "No payment page pattern. There's no example showing amount-due, payment method selector, payee/payor, terms, submit-and-receipt.",
            "No dispute path pattern. Many fines have a 'pay or dispute' choice on the same surface.",
            "No receipt page pattern.",
            "No look-up-then-pay pattern. Many fines require finding your fine first.",
        ],
        "proposed_examples": [
            {"concept": "Lookup-and-pay", "rationale": "Two-step flow: find the obligation, then pay it."},
            {"concept": "Pay-or-dispute", "rationale": "Page that presents amount and a clear branch to dispute."},
            {"concept": "Payment receipt", "rationale": "Confirmation page with downloadable proof."},
            {"concept": "Account-balance view", "rationale": "For multi-payment obligations (royalties, taxes), a balance-and-history page."},
        ],
        "note": "This service type likely earns its own productType in a future PR — payment is structurally distinct from public-form.",
    },
    {
        "id": "check-status-or-records",
        "name": "Check your status or records",
        "service_task": "Check",
        "kate_tarling_intents": ["checking-information"],
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
            "No authenticated-account-home pattern.",
            "No history/timeline pattern.",
            "No status-with-action-affordance pattern. Often the status check leads to action (apply for deferral, dispute charge).",
            "No record-detail pattern.",
        ],
        "proposed_examples": [
            {"concept": "My-account home", "rationale": "Landing page with status cards, recent activity, and quick actions."},
            {"concept": "History timeline", "rationale": "List of past events (payments, decisions, applications) with filters and detail-view links."},
            {"concept": "Record detail with actions", "rationale": "Page showing one record's full info with contextual actions (renew, dispute, download)."},
        ],
        "note": "Likely needs an account / portal productType beyond workspace and public-form.",
    },
    {
        "id": "search-a-public-register",
        "name": "Search a public register",
        "service_task": "Find",
        "kate_tarling_intents": ["checking-information"],
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
            "No verify-a-fact pattern. 'Is this professional registered?' is yes/no with details.",
            "No paid-search-with-payment pattern. Court records and land titles cost money.",
            "No record-citation pattern. Records often need to be cited (legal proceedings, applications).",
        ],
        "proposed_examples": [
            {"concept": "Verification result", "rationale": "'We found one match; here's what they're authorized to do' — yes/no with detail."},
            {"concept": "Paid-record retrieval", "rationale": "Three-step pattern: search → confirm + pay → retrieve."},
            {"concept": "Citation-ready record view", "rationale": "Printable, downloadable, or share-link pattern."},
        ],
    },
    {
        "id": "find-a-service-or-place",
        "name": "Find a service or place",
        "service_task": "Find",
        "kate_tarling_intents": ["checking-information"],
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
            "No location-based-search pattern. 'Near me' is common — no example handles geolocation or postal code with results map.",
            "No filter-by-criteria pattern for a directory.",
            "No directory-card-with-contact-info pattern with the standard facts.",
            "No no-results-with-recovery pattern.",
        ],
        "proposed_examples": [
            {"concept": "Directory search page", "rationale": "Combined filters + results in a public-facing directory shape."},
            {"concept": "Provider/place card", "rationale": "Standard result card with name, location, hours, contact, eligibility, accessibility."},
            {"concept": "Empty state with recovery", "rationale": "No-results pattern that suggests broader searches or contact."},
            {"concept": "Result detail page", "rationale": "Click-through view of one provider with full info."},
        ],
    },
    {
        "id": "access-an-in-person-program",
        "name": "Access an in-person program",
        "service_task": "Advise",
        "kate_tarling_intents": ["financial-support", "protecting"],
        "intent_note": "Multi-intent. Emergency $ supports lean financial-support; shelter/crisis services lean protecting.",
        "shared_shape": "Service exists but has no digital channel — citizen finds the program, calls or visits in person, gets human-mediated intake, receives the service. The digital surface (if any) is find-a-service-or-place shaped pointing at the program.",
        "variations": "Emergency/crisis services (shelter, evacuation support, crisis lines) vs. specialized in-person supports (food bank, addiction treatment, brain injury). Concentrated in ALSS/SCSS plus MHA, JUS, CFS.",
        "product_types_used": [],
        "matcher": matches_access_in_person,
        "existing_examples": [],
        "interaction_examples": [],
        "gaps": [
            "By definition this is the gap. ~11% of Alberta services have no digital channel.",
        ],
        "proposed_examples": [],
        "note": "No new examples in this brief. Brief 07 should surface this category as 'services without a digital surface; design system can't help build for these until digitization decision is made.' The forward-looking response is intake-and-assess productType pairs (worker side), pursued in a follow-up brief per scope.",
    },
    {
        "id": "read-information-or-guidance",
        "name": "Read information or guidance",
        "service_task": "Find",
        "kate_tarling_intents": ["checking-information"],
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
            "No structured-guidance page pattern.",
            "No 'rules and rights' pattern.",
            "No content-with-tools pattern (calculators, eligibility checkers embedded in guidance).",
        ],
        "proposed_examples": [
            {"concept": "Long-form guidance page", "rationale": "Standard structure for explanatory content."},
            {"concept": "Rules-and-rights page", "rationale": "Specific pattern for rights/obligations content."},
            {"concept": "Inline calculator", "rationale": "Mini-tool embedded in guidance."},
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


def build_artifact(assignments, args):
    cross_cutting_gaps = [
        {
            "id": "eligibility-checking",
            "name": "Eligibility checking before applying",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "apply-for-a-grant-or-funding"],
            "summary": "Citizens need to know if they qualify before starting an application. No canonical pattern.",
        },
        {
            "id": "status-tracking",
            "name": "Status tracking after submission",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "apply-for-a-grant-or-funding", "report-a-concern-or-incident", "file-a-complaint", "appeal-a-decision"],
            "summary": "result-page covers the immediate confirmation, not the long wait for a decision.",
        },
        {
            "id": "save-and-return",
            "name": "Save and return across sessions",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-grant-or-funding", "apply-for-a-licence-or-permit"],
            "summary": "Long applications can't be done in one sitting; the public-form template assumes one session.",
        },
        {
            "id": "account-or-portal",
            "name": "Authenticated account home / portal",
            "applies_to": ["check-status-or-records", "apply-for-a-licence-or-permit", "appeal-a-decision"],
            "summary": "No account/portal productType exists. check-status-or-records can't be served without one. Renewal sub-shape inside apply-for-a-licence-or-permit also depends on this.",
        },
        {
            "id": "payment-step",
            "name": "Payment as a step in a flow",
            "applies_to": ["apply-for-a-licence-or-permit", "search-a-public-register", "pay-a-fee-or-fine"],
            "summary": "No payment productType. Payment couples with licence applications and renewals, paid registry searches, fees and fines.",
        },
        {
            "id": "notifications-and-follow-up",
            "name": "Notifications and follow-up",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "report-a-concern-or-incident", "file-a-complaint"],
            "summary": "Every Apply-shape generates notifications (received, status changed, decision issued, renewal reminder). No notification example covers this depth.",
        },
        {
            "id": "decision-letters",
            "name": "Decision letters",
            "applies_to": ["apply-for-a-benefit", "apply-for-a-licence-or-permit", "apply-for-a-grant-or-funding", "file-a-complaint", "appeal-a-decision"],
            "summary": "result-page is the only candidate and it's thin for the complexity of decision/outcome content.",
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

        entry = {
            "id": st["id"],
            "name": st["name"],
            "service_task": st["service_task"],
            "kate_tarling_intents": st["kate_tarling_intents"],
            "leverage": {
                "service_count": len(members),
                "ministry_count": len(ministries),
                "passes_bar": passes,
            },
            "shared_shape": st["shared_shape"],
            "variations": st["variations"],
            "product_types_used": st.get("product_types_used", []),
            "existing_examples": st.get("existing_examples", []),
            "interaction_examples": st.get("interaction_examples", []),
            "gaps": st.get("gaps", []),
            "proposed_examples": st.get("proposed_examples", []),
            "services": services_field,
        }
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
        "$schema_version": "0.1",
        "jurisdiction": "ab",
        "generated": date.today().isoformat(),
        "purpose": "Service-type analysis of Alberta ministry maps. Each type is a (service task × Kate Tarling intent) cluster validated by the leverage bar (5+ services across 3+ ministries). Consumed by the design-system MCP, the using-goa-design-system skill, and the docs site service-type pages (Brief 07).",
        "service_tasks": SERVICE_TASKS,
        "kate_tarling_intents": KATE_TARLING_INTENTS,
        "service_types": service_types_out,
        "cross_cutting_gaps": cross_cutting_gaps,
        "excluded_or_below_bar": excluded_or_below_bar,
        "source": {
            "data_dir": "data/ab/",
            "method": "phase-1-classification of 637 supporting services by primary service task (channel-based with name-pattern overrides), then phase-2 clustering by name pattern within each task with leverage bar applied.",
            "constraints_applied": [
                "Citizen-side only. Worker-side service types (intake-and-assess, case management) deferred to a follow-up brief.",
                "Brief 12 product demo patterns NOT used as input to avoid biasing the system view.",
                "Size-agnostic example proposals — captures the concept rather than the size class.",
            ],
        },
    }

    return artifact, service_types_out


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


if __name__ == "__main__":
    main()
