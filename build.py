#!/usr/bin/env python3
"""
Build script for service-map-static
Processes seed data from service-map and generates JSON files for the static website.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple, Optional

# Channel type metadata (from the original database)
CHANNEL_TYPES = {
    "ch-transact": {"label": "Online transaction", "bg_color": "#c8e6c9", "text_color": "#1b5e20"},
    "ch-apply": {"label": "Apply", "bg_color": "#b2dfdb", "text_color": "#004d40"},
    "ch-check": {"label": "Check / portal", "bg_color": "#b3e5fc", "text_color": "#01579b"},
    "ch-find": {"label": "Find / search", "bg_color": "#e8f5e9", "text_color": "#2e7d32"},
    "ch-app": {"label": "Mobile app", "bg_color": "#e0f2f1", "text_color": "#00695c"},
    "ch-phone": {"label": "Phone", "bg_color": "#fff3e0", "text_color": "#e65100"},
    "ch-email": {"label": "Email", "bg_color": "#fce4ec", "text_color": "#c62828"},
    "ch-mail": {"label": "Mail", "bg_color": "#f3e5f5", "text_color": "#6a1b9a"},
    "ch-inperson": {"label": "In person", "bg_color": "#e3f2fd", "text_color": "#1565c0"},
    "ch-registry": {"label": "Registry agent", "bg_color": "#fff8e1", "text_color": "#f57f17"},
    "ch-pdf": {"label": "PDF / form", "bg_color": "#ffebee", "text_color": "#b71c1c"},
    "ch-pub": {"label": "Publication", "bg_color": "#f5f5f5", "text_color": "#616161"},
    "ch-engage": {"label": "Engage", "bg_color": "#e1bee7", "text_color": "#6a1b9a"},
    "ch-web": {"label": "Website", "bg_color": "#e8eaf6", "text_color": "#283593"},
}

CHANNEL_FILTER_ORDER = [
    'ch-transact', 'ch-apply', 'ch-check', 'ch-find', 'ch-app',
    'ch-phone', 'ch-email', 'ch-mail', 'ch-inperson', 'ch-registry',
    'ch-pdf', 'ch-pub', 'ch-engage',
]

DIGITAL_CHANNELS = {'ch-transact', 'ch-apply', 'ch-check', 'ch-find', 'ch-engage', 'ch-app', 'ch-web', 'ch-email'}

USER_GROUP_ORDER = [
    'Individuals', 'Seniors', 'Families', 'Persons with disabilities',
    'General public', 'Organizations', 'Municipalities',
    'Indigenous communities', 'Industry & contractors',
    'Drivers & vehicle owners',
    'Service providers', 'Communities', 'Professionals',
]


class ServiceMapBuilder:
    """Builds service map JSON files from seed data."""

    def __init__(self, seed_data_dir: Path, output_dir: Path):
        self.seed_data_dir = seed_data_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Cache for looking up services by name
        self.service_name_to_info: Dict[str, Dict[str, Any]] = {}

    def log(self, message: str):
        """Print a log message."""
        print(message, flush=True)

    def load_json(self, path: Path) -> Optional[Dict[str, Any]]:
        """Load a JSON file, return None if it doesn't exist."""
        if not path.exists():
            self.log(f"WARNING: File not found: {path}")
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"ERROR loading {path}: {e}")
            return None

    def save_json(self, path: Path, data: Any):
        """Save data as pretty-printed JSON."""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.log(f"✓ Wrote {path}")
        except Exception as e:
            self.log(f"ERROR writing {path}: {e}")

    def collect_all_services(self, ministry_data: Dict[str, Any], prefix: str):
        """Walk through the ministry data and collect all services for lookup."""
        # Collect foundational services at ministry level
        for service in ministry_data.get("foundational_services", []):
            service_name = service.get("name")
            if service_name:
                self.service_name_to_info[service_name] = {
                    "type": "foundational",
                    "goal_number": None,
                    "goal_color": None,
                    "ms_number": None,
                    "ms_name": None,
                }

        # Walk through goals and main services
        for goal in ministry_data.get("goals", []):
            goal_number = goal.get("number")
            goal_color = goal.get("color")

            # Collect foundational services at goal level
            for service in goal.get("foundational_services", []):
                service_name = service.get("name")
                if service_name:
                    self.service_name_to_info[service_name] = {
                        "type": "foundational",
                        "goal_number": None,
                        "goal_color": None,
                        "ms_number": None,
                        "ms_name": None,
                    }

            # Walk through main services
            for main_service in goal.get("main_services", []):
                ms_number = main_service.get("number")
                ms_name = main_service.get("name")

                # Collect foundational services at main service level
                for service in main_service.get("foundational_services", []):
                    service_name = service.get("name")
                    if service_name:
                        self.service_name_to_info[service_name] = {
                            "type": "foundational",
                            "goal_number": None,
                            "goal_color": None,
                            "ms_number": None,
                            "ms_name": None,
                        }

                # Collect supporting services
                for supporting_service in main_service.get("supporting", []):
                    service_name = supporting_service.get("name")
                    if service_name:
                        self.service_name_to_info[service_name] = {
                            "type": "supporting",
                            "goal_number": goal_number,
                            "goal_color": goal_color,
                            "ms_number": ms_number,
                            "ms_name": ms_name,
                        }

    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Look up service info by name."""
        return self.service_name_to_info.get(service_name)

    def collect_channels_and_user_groups(self, ministry_data: Dict[str, Any]) -> Tuple[Set[str], Set[str]]:
        """Collect all channel types and user groups used in the ministry data."""
        channels = set()
        user_groups = set()

        for goal in ministry_data.get("goals", []):
            for main_service in goal.get("main_services", []):
                for supporting_service in main_service.get("supporting", []):
                    # Collect channels
                    for channel in supporting_service.get("channels", []):
                        channel_type = channel.get("type")
                        if channel_type:
                            channels.add(channel_type)

                    # Collect user groups
                    for user_group in supporting_service.get("user_groups", []):
                        if user_group:
                            user_groups.add(user_group)

        return channels, user_groups

    def build_channel_filters(self, channels: Set[str]) -> List[Dict[str, Any]]:
        """Build ordered channel filter array with metadata."""
        filters = []
        for channel_code in CHANNEL_FILTER_ORDER:
            if channel_code in channels and channel_code in CHANNEL_TYPES:
                metadata = CHANNEL_TYPES[channel_code]
                filters.append({
                    "code": channel_code,
                    "label": metadata["label"],
                    "bg_color": metadata["bg_color"],
                    "text_color": metadata["text_color"],
                })
        return filters

    def build_user_group_filters(self, user_groups: Set[str]) -> List[str]:
        """Build ordered user group filter array."""
        filters = []
        # Add groups in order
        for group in USER_GROUP_ORDER:
            if group in user_groups:
                filters.append(group)
        # Add any remaining groups alphabetically
        remaining = sorted(user_groups - set(filters))
        filters.extend(remaining)
        return filters

    def add_goal_css_classes(self, ministry_data: Dict[str, Any]):
        """Add CSS class names to goals (goal-1, goal-2, etc.)."""
        for goal in ministry_data.get("goals", []):
            goal_number = goal.get("number")
            if goal_number:
                goal["css_class"] = f"goal-{goal_number}"

    def process_ministry(self, prefix: str) -> bool:
        """Process a single ministry (tec or alss)."""
        self.log(f"\nProcessing ministry: {prefix}")

        # Load seed data
        ministry_file = self.seed_data_dir / f"{prefix}.json"
        legislation_file = self.seed_data_dir / f"{prefix}_legislation_sections.json"

        ministry_data = self.load_json(ministry_file)
        legislation_data = self.load_json(legislation_file)

        if not ministry_data:
            self.log(f"ERROR: Could not load ministry data for {prefix}")
            return False

        # Clear the service lookup cache for this ministry
        self.service_name_to_info.clear()

        # Collect all services in this ministry
        self.collect_all_services(ministry_data, prefix)

        # Collect channels and user groups
        channels, user_groups = self.collect_channels_and_user_groups(ministry_data)

        # Build filters
        channel_filters = self.build_channel_filters(channels)
        user_group_filters = self.build_user_group_filters(user_groups)

        # Add computed fields to ministry data
        ministry_data["channel_filters"] = channel_filters
        ministry_data["user_group_filters"] = user_group_filters
        ministry_data["channel_types"] = CHANNEL_TYPES
        ministry_data["digital_channels"] = list(DIGITAL_CHANNELS)

        # Add CSS classes to goals
        self.add_goal_css_classes(ministry_data)

        # Save ministry data
        ministry_output = self.output_dir / f"{prefix}.json"
        self.save_json(ministry_output, ministry_data)

        # Process and save legislation data if it exists
        if legislation_data:
            self.log(f"Processing legislation for {prefix}")
            legislation_output_data = self.build_legislation_data(
                ministry_data, legislation_data, prefix
            )
            legislation_output = self.output_dir / f"{prefix}_legislation.json"
            self.save_json(legislation_output, legislation_output_data)

        return True

    def build_legislation_data(
        self,
        ministry_data: Dict[str, Any],
        legislation_data: Dict[str, Any],
        prefix: str
    ) -> Dict[str, Any]:
        """Build the legislation output data with cross-references."""

        output = {
            "prefix": prefix,
            "name": ministry_data.get("full_name", ""),
            "short_name": ministry_data.get("short_name", ""),
            "goals": [],
            "acts": [],
            "stats": {
                "acts_count": 0,
                "sections_count": 0,
                "services_with_leg_count": 0,
                "services_multi_act_count": 0,
            }
        }

        # Build goals summary for legislation
        for goal in ministry_data.get("goals", []):
            goal_summary = {
                "number": goal.get("number"),
                "color": goal.get("color"),
                "short_name": goal.get("short_name"),
                "legend_label": goal.get("legend_label"),
                "main_services": []
            }

            for main_service in goal.get("main_services", []):
                ms_summary = {
                    "number": main_service.get("number"),
                    "name": main_service.get("name"),
                }
                goal_summary["main_services"].append(ms_summary)

            output["goals"].append(goal_summary)

        # Track services with legislation for stats
        services_with_leg = set()
        services_in_multiple_acts = set()

        # Process acts and sections
        for act in legislation_data.get("acts", []):
            act_abbrev = act.get("abbrev")
            act_summary = {
                "abbrev": act_abbrev,
                "full_name": act.get("full_name", ""),
                "color": act.get("color", "#000000"),
                "citation": act.get("citation", ""),
                "summary": act.get("summary", ""),
                "full_text": act.get("full_text", ""),
                "sections": []
            }

            for section in act.get("sections", []):
                section_output = {
                    "ref": section.get("ref"),
                    "title": section.get("title"),
                    "description": section.get("description"),
                    "anchor_id": section.get("anchor_id"),
                    "services": []
                }

                # Look up each service mentioned in this section
                for service_name in section.get("services", []):
                    service_info = self.get_service_info(service_name)

                    if service_info:
                        services_with_leg.add(service_name)

                        service_output = {
                            "type": service_info["type"],
                            "name": service_name,
                            "goal_number": service_info["goal_number"],
                            "goal_color": service_info["goal_color"],
                            "ms_number": service_info["ms_number"],
                            "ms_name": service_info["ms_name"],
                        }
                        section_output["services"].append(service_output)

                if section_output["services"]:
                    act_summary["sections"].append(section_output)

            output["acts"].append(act_summary)

        # Calculate stats
        output["stats"]["acts_count"] = len(output["acts"])
        output["stats"]["sections_count"] = sum(
            len(act["sections"]) for act in output["acts"]
        )
        output["stats"]["services_with_leg_count"] = len(services_with_leg)

        # Find services in multiple acts
        service_act_count: Dict[str, int] = {}
        for act in output["acts"]:
            unique_services_in_act = set()
            for section in act["sections"]:
                for service in section["services"]:
                    unique_services_in_act.add(service["name"])

            for service_name in unique_services_in_act:
                service_act_count[service_name] = service_act_count.get(service_name, 0) + 1

        for service_name, count in service_act_count.items():
            if count > 1:
                services_in_multiple_acts.add(service_name)

        output["stats"]["services_multi_act_count"] = len(services_in_multiple_acts)

        return output

    def build_ministries_index(self) -> bool:
        """Build the ministries.json index file."""
        self.log("\nBuilding ministries index")

        # Load ministry data files
        tec_data = self.load_json(self.seed_data_dir / "tec.json")
        alss_data = self.load_json(self.seed_data_dir / "alss.json")

        ministries = []

        if tec_data:
            ministries.append({
                "prefix": "tec",
                "name": tec_data.get("full_name", ""),
                "short_name": tec_data.get("short_name", ""),
                "blurb": tec_data.get("blurb", ""),
            })

        if alss_data:
            ministries.append({
                "prefix": "alss",
                "name": alss_data.get("full_name", ""),
                "short_name": alss_data.get("short_name", ""),
                "blurb": alss_data.get("blurb", ""),
            })

        if ministries:
            output_file = self.output_dir / "ministries.json"
            self.save_json(output_file, ministries)
            return True
        else:
            self.log("ERROR: No ministry data found")
            return False

    def run(self) -> bool:
        """Run the full build process."""
        self.log("=" * 60)
        self.log("Service Map Static Build")
        self.log("=" * 60)

        success = True

        # Build ministries index
        if not self.build_ministries_index():
            success = False

        # Process each ministry
        for prefix in ["tec", "alss"]:
            if not self.process_ministry(prefix):
                success = False

        self.log("\n" + "=" * 60)
        if success:
            self.log("✓ Build completed successfully")
        else:
            self.log("✗ Build completed with errors")
        self.log("=" * 60)

        return success


def main():
    """Main entry point."""
    # Get the directory of this script
    script_dir = Path(__file__).parent

    # Paths
    seed_data_dir = script_dir.parent / "service-map" / "seed_data"
    output_dir = script_dir / "data"

    # Validate seed data directory exists
    if not seed_data_dir.exists():
        print(f"ERROR: Seed data directory not found: {seed_data_dir}", file=sys.stderr)
        return 1

    # Run builder
    builder = ServiceMapBuilder(seed_data_dir, output_dir)
    success = builder.run()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
