# Ministry Service Map Schema — {prefix}.json

## Top-level fields

```json
{
  "prefix": "cfs",                    // 2-4 letter code, lowercase, matches folder name
  "full_name": "Children and Family Services",
  "short_name": "Children & Family Services",
  "blurb": "One to two sentences...",
  "nav_name": "Children and Family Services",  // Name shown in navigation
  "has_registry_agents": false,        // true if services are delivered via registry agents
  "goals": [],                         // Array of Goal objects (see below)
  "foundational_services": [],         // Ministry-level foundational services (optional)
  "mandate_legend": {},                // Mandate letter tag definitions (optional)
  "channel_filters": [],               // Computed: unique channel types across all services
  "user_group_filters": [],            // Computed: unique user groups across all services
  "digital_channels": []               // Computed: channel type codes where digital=true
}
```

## Goal object

```json
{
  "number": 1,                         // Sequential, 1-based
  "color": "#0070c0",                  // Hex color for the goal's visual indicator
  "title": "OUTCOME 1: Addressing Needs",  // Full title shown in header
  "short_name": "Services and supports are accessible and responsive",
  "legend_label": "Addressing needs",  // Short label for legend/filters
  "description": "Paragraph describing the outcome...",
  "main_services": [],                 // Array of Main Service objects
  "foundational_services": []          // Goal-level foundational services (optional)
}
```

## Main Service object

```json
{
  "number": 1,                         // Sequential within the goal, 1-based
  "name": "Report and respond to child safety concerns",
  "supporting": [],                    // Array of Supporting Service objects
  "foundational_services": []          // Service-level foundational services (optional)
}
```

## Supporting Service object

This is the core unit — it represents a specific thing a citizen can do.

```json
{
  "name": "Report concerns about child abuse or neglect",
  "desc": "Anyone who suspects a child is being abused or neglected is legally required to report it.",
  "users": "Anyone concerned about a child's safety",
  "user_groups": ["General public", "Families"],
  "reach": {
    "tier": "high",                    // One of: very_high, high, medium, low
    "estimate": "~30,000 reports/yr",  // Human-readable volume
    "basis": "annual"                  // "annual", "monthly", or "one-time"
  },
  "economic_impact": {
    "tag": "Cost avoidance",           // Human-readable label
    "category": "cost_avoidance",      // Must match a key in config.json impact_categories
    "note": "Early identification prevents escalation..."
  },
  "channels": [
    {
      "type": "ch-phone",             // Must match a key in config.json channel_types
      "label": "Child Abuse Hotline: 1-800-387-5437 (24/7)",
      "url": null                     // URL for digital channels, null for non-digital
    },
    {
      "type": "ch-find",
      "label": "alberta.ca/child-intervention",
      "url": "https://www.alberta.ca/how-child-intervention-works"
    }
  ],
  "legislation": [
    {
      "abbrev": "CYFEA",
      "color": "#0070c0",
      "full_name": "Child, Youth and Family Enhancement Act"
    }
  ],
  "mandate_tags": [
    {
      "number": 3,
      "text": "Review the Child, Youth and Family Enhancement Act"
    }
  ]
}
```

## Computed filter arrays

These are derived from the data and placed at the top level of the ministry JSON. They power the filter UI on the service map page.

**channel_filters**: Deduplicated list of all channel types used across all supporting services.
```json
"channel_filters": ["ch-phone", "ch-find", "ch-web", "ch-inperson", "ch-apply"]
```

**user_group_filters**: Deduplicated list of all user groups.
```json
"user_group_filters": ["General public", "Families", "Seniors", "Youth"]
```

**digital_channels**: List of channel type codes where `digital: true` in config.json.
```json
"digital_channels": ["ch-transact", "ch-apply", "ch-check", "ch-find", "ch-engage", "ch-app", "ch-web", "ch-email"]
```

## Foundational services

These are internal or cross-cutting capabilities that support multiple citizen-facing services but aren't directly accessed by the public. They appear at three levels:

- **Ministry level**: Applies to the whole ministry (e.g., "IT shared services")
- **Goal level**: Applies to all services under that goal
- **Main service level**: Applies to services in that grouping

```json
"foundational_services": [
  "Oversee delegated child intervention agencies"
]
```

## Mandate legend

Maps mandate tag numbers to their text, providing a legend for the mandate letter references.

```json
"mandate_legend": {
  "M1": "Support community-based child welfare organizations",
  "M3": "Review the Child, Youth and Family Enhancement Act"
}
```
