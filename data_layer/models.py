"""
Domain models — plain dataclasses with no backend dependency.
These are the contract between the interface and any backend implementation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ── Jurisdiction ──────────────────────────────────────────────

@dataclass
class Jurisdiction:
    code: str                          # "goa", "calgary"
    name: str                          # "Government of Alberta"
    short_name: str                    # "Alberta"
    country: str                       # "CA"
    type: str                          # "province", "municipality", "federal"
    parent: Optional[str] = None       # parent jurisdiction code, if any
    path: Optional[str] = None         # filesystem path, e.g. "ca/ab/goa"

    # Config (from config.json)
    brand_color: str = "#00405c"
    brand_color_light: Optional[str] = None
    accent_color: Optional[str] = None
    org_unit_label: str = "Ministry"   # "Ministry", "Corporation", "Department"
    goal_label: str = "Outcome"
    main_service_label: str = "Main Service"
    last_updated: Optional[str] = None
    legislation_source: Optional[str] = None
    mandate_source_type: Optional[str] = None

    # Channel type definitions (shared across entities in this jurisdiction)
    channel_types: dict = field(default_factory=dict)
    # Reach tiers / impact categories (optional config)
    reach_tiers: Optional[dict] = None
    impact_categories: Optional[dict] = None


# ── Entity (Ministry / Corporation / Department) ──────────────

@dataclass
class Entity:
    prefix: str                        # "tec", "enmax"
    jurisdiction_code: str             # "ab", "calgary"
    name: str                          # full name
    short_name: str                    # display name
    blurb: Optional[str] = None
    nav_name: Optional[str] = None     # sidebar nav label
    has_registry_agents: bool = False
    is_test: bool = False

    # Mandate metadata
    mandate_date: Optional[str] = None
    mandate_minister: Optional[str] = None
    mandate_pdf: Optional[str] = None
    cross_cutting: list[str] = field(default_factory=list)
    mandate_legend: list[dict] = field(default_factory=list)


# ── Goal ──────────────────────────────────────────────────────

@dataclass
class Goal:
    id: Optional[int] = None           # DB primary key
    entity_prefix: str = ""
    jurisdiction_code: str = ""
    number: int = 0
    color: str = ""
    title: str = ""
    short_name: str = ""
    legend_label: str = ""
    description: str = ""


# ── Main Service ──────────────────────────────────────────────

@dataclass
class MainService:
    id: Optional[int] = None
    goal_id: Optional[int] = None
    number: int = 0
    name: str = ""


# ── Supporting Service ────────────────────────────────────────

@dataclass
class SupportingService:
    id: Optional[int] = None
    main_service_id: Optional[int] = None
    name: str = ""
    desc: Optional[str] = None
    users: Optional[str] = None
    user_groups: list[str] = field(default_factory=list)
    channels: list[Channel] = field(default_factory=list)
    legislation: list[LegislationRef] = field(default_factory=list)
    mandate_tags: list[str] = field(default_factory=list)
    taxonomy: Optional[Taxonomy] = None


# ── Foundational Service ──────────────────────────────────────

@dataclass
class FoundationalService:
    id: Optional[int] = None
    # Parent can be entity, goal, or main_service
    parent_type: str = ""              # "entity", "goal", "main_service"
    parent_id: Optional[int] = None    # FK to the parent's DB id
    # Some foundational services are just strings (legacy)
    is_string: bool = False
    string_value: Optional[str] = None
    # Full object fields
    source_id: Optional[str] = None    # original "id" field like "f-6"
    name: str = ""
    desc: Optional[str] = None
    users: Optional[str] = None
    user_groups: list[str] = field(default_factory=list)
    channels: list[Channel] = field(default_factory=list)
    legislation: list[LegislationRef] = field(default_factory=list)
    mandate_tags: list[str] = field(default_factory=list)
    taxonomy: Optional[Taxonomy] = None


# ── Channel ───────────────────────────────────────────────────

@dataclass
class Channel:
    type: str                          # "ch-phone", "ch-web", etc.
    label: str = ""
    url: Optional[str] = None


# ── Legislation Reference (inline on a service) ──────────────

@dataclass
class LegislationRef:
    abbrev: str = ""
    color: str = ""
    full_name: str = ""


# ── Taxonomy Classification ───────────────────────────────────

@dataclass
class Taxonomy:
    track: str = ""                    # "individual", "business", "both"
    # Single-track fields
    tier: Optional[str] = None
    domain: Optional[str] = None
    # Both-track fields
    individual_tier: Optional[str] = None
    individual_domain: Optional[str] = None
    business_tier: Optional[str] = None
    business_domain: Optional[str] = None
    # Relationships
    relationships: list[Relationship] = field(default_factory=list)


@dataclass
class Relationship:
    type: str = ""                     # "worker_employer", etc.
    service: str = ""                  # target service name
    ministry: str = ""                 # target entity prefix (may be jurisdiction-qualified)


# ── Legislation Cross-Reference ───────────────────────────────

@dataclass
class Act:
    id: Optional[int] = None
    entity_prefix: str = ""
    jurisdiction_code: str = ""
    abbrev: str = ""
    full_name: str = ""
    color: str = ""
    citation: Optional[str] = None
    summary: Optional[str] = None
    full_text: Optional[str] = None
    sort_order: int = 0


@dataclass
class ActSection:
    id: Optional[int] = None
    act_id: Optional[int] = None
    ref: str = ""
    title: str = ""
    description: str = ""
    anchor_id: str = ""
    sort_order: int = 0


@dataclass
class SectionService:
    section_id: Optional[int] = None
    service_name: str = ""
    service_type: str = ""             # "supporting", "foundational"
    goal_number: Optional[int] = None
    goal_color: str = ""
    ms_number: Optional[int] = None
    ms_name: str = ""
