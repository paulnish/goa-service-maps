---
name: service-map-collector
description: >
  Collect and structure government service map data for any ministry or jurisdiction.
  Use this skill whenever the user wants to: add a new ministry to the service map,
  add a new jurisdiction (province, state, territory, federal), research government
  services for a department, populate service map JSON, create legislation cross-references,
  or update existing ministry data. Also triggers when the user mentions "service map",
  "ministry data", "government services research", "Kate Tarling", or any government
  department name in the context of service delivery mapping.
---

# Service Map Data Collector

You are a research agent that collects and structures data about how government organizations deliver services to the public, following the Kate Tarling service mapping framework.

## The Framework

Government service delivery follows a hierarchy:

```
Jurisdiction (e.g., Alberta)
└── Ministry / Department
    └── Goals (outcomes the ministry is trying to achieve)
        └── Main Services (groupings of related service delivery)
            └── Supporting Services (the actual things citizens interact with)
                ├── Channels (how citizens access the service)
                ├── Legislation (legal authority for the service)
                └── Mandate tags (links to ministerial mandate letters)
```

The distinction between main services and supporting services is important. A main service is a label for a group of related delivery activities. A supporting service is a specific thing a citizen can do — "Apply for student aid", "Report a pothole", "Register a vehicle". Supporting services always have channels (the touchpoints where delivery happens).

## Before You Start

1. Read the jurisdiction's `config.json` to understand vocabulary, channel types, and branding
2. Read `ministries.json` to see what already exists
3. If adding to an existing ministry, read the current `{prefix}.json` to understand the existing structure

The data lives at: `data/{jurisdiction_code}/`

## Phase 1: Reconnaissance

Research the ministry or department to understand its mandate and organizational structure.

**Sources to check (in priority order):**
- The government's official website for the ministry/department
- Mandate letters or ministerial orders (these define the goals)
- Annual reports and business plans (these define outcomes and performance measures)
- Organizational charts
- Budget estimates (these reveal the relative scale of programs)

**What you're looking for:**
- The ministry's full name, short name, and a 1-2 sentence blurb
- A suitable prefix (2-4 lowercase letters, e.g., "tec", "cfs", "edu")
- 2-5 high-level goals or outcomes (often mapped directly from mandate letters or business plans)
- The major program areas (these become main services)

Write your findings to a scratch notes file. Don't start populating JSON yet — get the big picture first and confirm it with the user.

## Phase 2: Ministry Deep Dive

For each goal, identify the main services and their supporting services.

**For each supporting service, collect:**

| Field | What to capture | Where to find it |
|-------|----------------|------------------|
| `name` | Action-oriented, citizen-facing (e.g., "Apply for student aid") | Ministry website service pages |
| `desc` | 1-2 sentence plain-language description | Service pages, program descriptions |
| `users` | Who uses this (e.g., "Students", "Employers") | Service pages |
| `user_groups` | Array of group labels for filtering | Derive from users field |
| `channels` | How citizens access it (see Channel Types below) | Service pages, contact pages |
| `reach` | Usage volume estimate with tier | Annual reports, FOIP, estimates |
| `economic_impact` | Category and note about economic effect | Budget docs, program evaluations |

**Channel collection rules:**
- Always capture the specific URL for digital channels (not just "website")
- Phone numbers should include the full number and hours if available
- Distinguish between transactional channels (ch-transact, ch-apply) and informational ones (ch-web, ch-find)
- Check config.json for the jurisdiction's defined channel types — only use types that exist there

**Naming conventions for services:**
- Start with a verb: "Apply for…", "Register a…", "Report…", "Find…", "Get…", "Check…"
- Write from the citizen's perspective, not the government's
- Avoid bureaucratic language — "Get help with housing" not "Access Housing Stability Program supports"

## Phase 3: Legislation Cross-Reference

This phase maps which legislation authorizes each service. It produces a separate `{prefix}_legislation.json` file.

**For each act that governs the ministry:**
1. Identify the act's full name, abbreviation, and a color for the legend
2. Find the specific sections that relate to each supporting service
3. For each section, record: reference (e.g., "s.2"), title, and a plain-language description
4. Map each section to the supporting services it authorizes

**Legislation research sources:**
- For Canadian provinces: the province's Queen's/King's Printer website
- For Canadian federal: laws-lois.justice.gc.ca
- For US states: the state legislature's website
- CanLII (canlii.org) for searchable full text of Canadian legislation

**Full text collection:**
If possible, obtain the full text of each act and inject HTML anchor spans so the legislation drawer can scroll to specific sections. The anchor format is:
```html
<span id="anchor-{act_abbrev_lower}-{section_ref}"></span>
```

This is time-intensive. Do it for the most important acts first (the ones that touch the most services), and flag the rest as needing full text later.

## Phase 4: Validation

Before presenting the final data to the user, run the bundled validator script to check:

1. **Schema compliance**: Every supporting service has name, desc, users, user_groups, channels (non-empty array)
2. **Channel validity**: Every channel type exists in config.json's channel_types
3. **Legislation consistency**: Every act/section in the legislation JSON maps to a service that actually exists in the ministry JSON, and vice-versa (services with legislation[] entries should appear in the legislation JSON)
4. **No orphans**: Every supporting service belongs to a main service, every main service to a goal
5. **Filter arrays**: channel_filters and user_group_filters are computed from the actual data
6. **Reach coverage**: At least 80% of supporting services have a reach estimate
7. **Naming**: All supporting service names start with a verb

Run the validator like this:

```bash
# Validate a specific ministry
python scripts/validate.py <path-to-data-dir> --jurisdiction ab --ministry cfs

# Validate all ministries in a jurisdiction
python scripts/validate.py <path-to-data-dir> --jurisdiction ab

# Validate every jurisdiction
python scripts/validate.py <path-to-data-dir>
```

The script prints each issue with its location and severity (`✗` for errors that will likely break the site, `⚠` for warnings worth reviewing). It exits with code 0 if there are no errors, 1 otherwise.

Don't just run the validator and hand over the results — read them carefully and fix the real issues before presenting the data. The naming warnings are heuristic (based on a verb list) and some false positives are expected; use judgment.

## Output File Schemas

### {prefix}.json — Ministry Service Map

Read `references/ministry-schema.md` for the complete schema with all fields documented.

### {prefix}_legislation.json — Legislation Cross-Reference

Read `references/legislation-schema.md` for the complete schema.

### ministries.json entry

```json
{
  "prefix": "cfs",
  "name": "Children and Family Services",
  "short_name": "Children & Family Services",
  "blurb": "One to two sentences describing what the ministry does for citizens."
}
```

### config.json (for new jurisdictions only)

Read `references/config-schema.md` for the jurisdiction configuration schema.

## Adding a New Ministry (to an existing jurisdiction)

1. Run phases 1-4 above
2. Write `data/{code}/{prefix}.json`
3. Optionally write `data/{code}/{prefix}_legislation.json`
4. Add the ministry entry to `data/{code}/ministries.json`
5. If the site uses per-ministry HTML (like goa-service-maps), create the page files:
   - Copy an existing `{prefix}/service-map.html` and update the default prefix
   - Copy `{prefix}/legislation.html` if legislation data exists
   - Add redirect rules to `netlify.toml`
6. Present the validation report to the user

## Adding a New Jurisdiction

1. Identify the jurisdiction code (2-letter for provinces/states, 3-letter for countries)
2. Create `data/{code}/config.json` — start from an existing config.json (like Alberta's) and adapt:
   - Jurisdiction identity fields (name, type, country)
   - Brand colors (from the government's official website/style guide)
   - Channel types (most will be the same; some jurisdictions have unique ones like "ServiceOntario kiosk")
   - Vocabulary labels (e.g., BC uses "Ministry", Ontario uses "Ministry", US states use "Department", federal uses "Department")
   - Reach tiers and impact categories can usually stay the same
3. Create `data/{code}/ministries.json` (start empty: `[]`)
4. Add the jurisdiction to the top-level `data/jurisdictions.json`
5. Then add ministries one at a time using the process above

## Quality Standards

- **Citizen perspective**: Everything is written from the perspective of someone trying to get something done, not from the government's internal perspective
- **Verifiable**: Every fact should be traceable to a published government source — annual reports, websites, legislation
- **Complete channels**: If a service exists, there must be at least one channel. If you can't find one, flag it rather than omitting the service
- **Honest reach estimates**: Use "unknown" tier rather than guessing. Budget documents and annual reports are the most reliable sources
- **Act names**: Always use the official short title of legislation, not informal names
