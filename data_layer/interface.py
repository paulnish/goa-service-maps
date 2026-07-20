"""
Abstract data access interface.

Any backend (SQLite, Postgres, API, flat files) implements this protocol.
Consuming code depends only on this interface — never on a specific backend.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from data_layer.models import (
    Jurisdiction, Entity, Goal, MainService,
    SupportingService, FoundationalService,
    Act, ActSection, SectionService, Taxonomy,
)


class DataBackend(ABC):
    """Contract that every data backend must fulfill."""

    # ── Lifecycle ─────────────────────────────────────────────

    @abstractmethod
    def initialize(self) -> None:
        """Create tables / collections / schema if they don't exist."""

    @abstractmethod
    def close(self) -> None:
        """Release resources."""

    # ── Jurisdictions ─────────────────────────────────────────

    @abstractmethod
    def upsert_jurisdiction(self, j: Jurisdiction) -> None: ...

    @abstractmethod
    def get_jurisdiction(self, code: str) -> Optional[Jurisdiction]: ...

    @abstractmethod
    def list_jurisdictions(self) -> list[Jurisdiction]: ...

    # ── Entities ──────────────────────────────────────────────

    @abstractmethod
    def upsert_entity(self, e: Entity) -> None: ...

    @abstractmethod
    def get_entity(self, prefix: str, jurisdiction_code: str) -> Optional[Entity]: ...

    @abstractmethod
    def list_entities(self, jurisdiction_code: str) -> list[Entity]: ...

    # ── Goals ─────────────────────────────────────────────────

    @abstractmethod
    def upsert_goal(self, g: Goal) -> int:
        """Returns the goal's DB id."""

    @abstractmethod
    def list_goals(self, entity_prefix: str, jurisdiction_code: str) -> list[Goal]: ...

    # ── Main Services ─────────────────────────────────────────

    @abstractmethod
    def upsert_main_service(self, ms: MainService) -> int:
        """Returns the main service's DB id."""

    @abstractmethod
    def list_main_services(self, goal_id: int) -> list[MainService]: ...

    # ── Supporting Services ───────────────────────────────────

    @abstractmethod
    def upsert_supporting_service(self, ss: SupportingService) -> int:
        """Returns the supporting service's DB id."""

    @abstractmethod
    def list_supporting_services(self, main_service_id: int) -> list[SupportingService]: ...

    # ── Foundational Services ─────────────────────────────────

    @abstractmethod
    def upsert_foundational_service(self, fs: FoundationalService) -> int:
        """Returns the foundational service's DB id."""

    @abstractmethod
    def list_foundational_services(self, parent_type: str, parent_id: int) -> list[FoundationalService]: ...

    # ── Legislation ───────────────────────────────────────────

    @abstractmethod
    def upsert_act(self, act: Act) -> int: ...

    @abstractmethod
    def list_acts(self, entity_prefix: str, jurisdiction_code: str) -> list[Act]: ...

    @abstractmethod
    def upsert_act_section(self, section: ActSection) -> int: ...

    @abstractmethod
    def list_act_sections(self, act_id: int) -> list[ActSection]: ...

    @abstractmethod
    def upsert_section_service(self, ss: SectionService) -> None: ...

    @abstractmethod
    def list_section_services(self, section_id: int) -> list[SectionService]: ...

    # ── Taxonomy (shared definition) ──────────────────────────

    @abstractmethod
    def set_taxonomy_definition(self, taxonomy_json: dict) -> None:
        """Store the full taxonomy.json structure."""

    @abstractmethod
    def get_taxonomy_definition(self) -> dict:
        """Retrieve the full taxonomy.json structure."""

    # ── Bulk Operations ───────────────────────────────────────

    @abstractmethod
    def import_jurisdiction_json(self, jurisdiction_code: str, data_dir: str) -> dict:
        """Import all JSON files for a jurisdiction from data_dir.
        Returns stats dict with counts of imported objects."""

    @abstractmethod
    def export_entity_json(self, entity_prefix: str, jurisdiction_code: str) -> dict:
        """Export a single entity as a dict matching the {prefix}.json format."""

    @abstractmethod
    def export_legislation_json(self, entity_prefix: str, jurisdiction_code: str) -> Optional[dict]:
        """Export legislation as a dict matching {prefix}_legislation.json. None if no legislation."""

    @abstractmethod
    def export_jurisdiction_config(self, jurisdiction_code: str) -> dict:
        """Export jurisdiction config.json."""

    @abstractmethod
    def export_entities_index(self, jurisdiction_code: str) -> list[dict]:
        """Export the ministries.json / entities.json index for a jurisdiction."""

    @abstractmethod
    def export_jurisdictions_index(self) -> list[dict]:
        """Export jurisdictions.json."""

    # ── Validation ────────────────────────────────────────────

    @abstractmethod
    def validate(self) -> list[str]:
        """Run integrity checks. Returns a list of warning/error strings.
        Empty list = all clear."""

    # ── Stats ─────────────────────────────────────────────────

    @abstractmethod
    def stats(self) -> dict:
        """Return summary counts: jurisdictions, entities, goals,
        main_services, supporting_services, foundational_services, acts, etc."""
