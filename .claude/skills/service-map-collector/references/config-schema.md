# Jurisdiction Configuration Schema — config.json

Each jurisdiction has a single `config.json` file at `data/{code}/config.json` that externalizes everything data-coupled: channel types, reach tiers, impact categories, vocabulary labels, and brand colors. This is what lets a single codebase render Alberta, British Columbia, Ontario, or any US state without hardcoding their differences.

When creating a new jurisdiction, copy Alberta's config.json as a starting point and adapt the fields below.

## Full schema

```json
{
  "jurisdiction": "ab",
  "jurisdiction_name": "Government of Alberta",
  "jurisdiction_short": "Alberta",
  "jurisdiction_type": "province",
  "country": "CA",
  "brand_color": "#00405c",
  "brand_color_light": "#d5e8f0",
  "accent_color": "#2e75b6",
  "last_updated": "2026-04",
  "legislation_source": "https://kings-printer.alberta.ca/documents/Acts/",
  "mandate_source_type": "mandate_letter",
  "org_unit_label": "Ministry",
  "goal_label": "Outcome",
  "main_service_label": "Main Service",
  "channel_types": { },
  "reach_tiers": { },
  "impact_categories": { }
}
```

## Identity fields

| Field | Type | Description |
|-------|------|-------------|
| `jurisdiction` | string | Short code matching the folder name. 2-letter for provinces/states (`ab`, `bc`, `ca`), 3-letter for countries (`can`, `usa`). Lowercase. |
| `jurisdiction_name` | string | Full official name. "Government of Alberta", "Province of British Columbia", "State of California". |
| `jurisdiction_short` | string | Short display name. "Alberta", "BC", "California". |
| `jurisdiction_type` | string | One of: `province`, `state`, `territory`, `federal`, `municipality`. |
| `country` | string | ISO 3166-1 alpha-2 country code. `CA`, `US`, `GB`, `AU`. |
| `last_updated` | string | YYYY-MM format. Flag stale configs to the user. |

## Branding

| Field | Type | Description |
|-------|------|-------------|
| `brand_color` | hex | Primary brand color, usually from the jurisdiction's official style guide. Used in headers and navigation. |
| `brand_color_light` | hex | Light tint of the brand color. Used for backgrounds and hover states. |
| `accent_color` | hex | Secondary color for highlights and links. |

**Where to find brand colors:**
- Canada (provincial): Most provinces publish visual identity guidelines. Search for "{province} visual identity guidelines" or inspect the official .gov website's CSS.
- US (state): Look for state branding guides or inspect the official .gov website.
- Federal Canada: https://www.canada.ca design system.
- Federal US: U.S. Web Design System tokens.

## Vocabulary labels

Different jurisdictions use different terminology. These fields let each jurisdiction render its own words.

| Field | Examples |
|-------|----------|
| `org_unit_label` | "Ministry" (Canadian provinces, UK), "Department" (US states, US federal), "Agency" (some federal agencies) |
| `goal_label` | "Outcome" (Alberta), "Goal", "Priority", "Strategic Objective" |
| `main_service_label` | "Main Service", "Service Line", "Program Area" |

When adapting for a new jurisdiction, read their annual reports and mandate documents to see which terms they use internally.

## Legislation source

| Field | Description |
|-------|-------------|
| `legislation_source` | Base URL for the jurisdiction's official legislation library (Queen's/King's Printer, State Code, etc.). Used as a fallback link and as the canonical source for full_text extraction. |
| `mandate_source_type` | One of: `mandate_letter` (Canadian provinces with public mandate letters), `business_plan`, `executive_order`, `strategic_plan`, `none`. Determines what kind of source the mandate_tags reference. |

## channel_types

The full set of channels citizens might use to access services. Each channel type has a code, a label, colors for rendering chips, and a `digital` boolean.

```json
"channel_types": {
  "ch-transact": { "label": "Online transaction", "bg": "#c8e6c9", "fg": "#1b5e20", "digital": true },
  "ch-apply":    { "label": "Apply", "bg": "#b2dfdb", "fg": "#004d40", "digital": true },
  "ch-check":    { "label": "Check / portal", "bg": "#b3e5fc", "fg": "#01579b", "digital": true },
  "ch-find":     { "label": "Find / search", "bg": "#e8f5e9", "fg": "#2e7d32", "digital": true },
  "ch-engage":   { "label": "Engage", "bg": "#e1bee7", "fg": "#6a1b9a", "digital": true },
  "ch-app":      { "label": "Mobile app", "bg": "#e0f2f1", "fg": "#00695c", "digital": true },
  "ch-web":      { "label": "Website", "bg": "#e8eaf6", "fg": "#283593", "digital": true },
  "ch-email":    { "label": "Email", "bg": "#fce4ec", "fg": "#c62828", "digital": true },
  "ch-phone":    { "label": "Phone", "bg": "#fff3e0", "fg": "#e65100", "digital": false },
  "ch-mail":     { "label": "Mail", "bg": "#f3e5f5", "fg": "#6a1b9a", "digital": false },
  "ch-inperson": { "label": "In person", "bg": "#e3f2fd", "fg": "#1565c0", "digital": false },
  "ch-registry": { "label": "Registry agent", "bg": "#fff8e1", "fg": "#f57f17", "digital": false, "border": "#f9a825" },
  "ch-pdf":      { "label": "PDF / form", "bg": "#ffebee", "fg": "#b71c1c", "digital": false },
  "ch-pub":      { "label": "Publication", "bg": "#f5f5f5", "fg": "#616161", "digital": false }
}
```

### Per-channel fields

| Field | Required | Description |
|-------|----------|-------------|
| `label` | yes | Human-readable name shown in filters and legends. |
| `bg` | yes | Background color of the channel chip. |
| `fg` | yes | Foreground (text) color of the channel chip. |
| `digital` | yes | Whether this channel counts as digital delivery. Used to compute the digital_channels array and for digital-only filters. |
| `border` | no | Optional border color, used to make a channel stand out (Alberta uses this for registry agents). |

### Channel type guidelines

**Reuse existing types when possible.** The 14 types above cover most citizen-facing government services. Before inventing a new type, check whether an existing one fits.

**When to add jurisdiction-specific types:**
- Ontario has `ServiceOntario` kiosks and storefronts as a distinct channel.
- Quebec has `Services Québec` offices.
- Some US states have dedicated in-person assistance programs.
- UK has GOV.UK Verify for identity.

If you add a jurisdiction-specific channel, document why in a comment (JSON doesn't support comments, so add a top-level `_notes` field if needed).

**Colors:** Use muted, accessible pairs. The backgrounds are light pastels and the foregrounds are the dark version of the same hue. Check contrast ratios to meet WCAG AA (4.5:1 for normal text).

## reach_tiers

Defines the volume tiers used when estimating how many people a service touches per year.

```json
"reach_tiers": {
  "very_high": { "label": "100K+", "color": "#1565c0" },
  "high":      { "label": "10K–100K", "color": "#2196f3" },
  "medium":    { "label": "1K–10K", "color": "#64b5f6" },
  "low":       { "label": "<1K", "color": "#90caf9" }
}
```

**Guidelines:**
- Keep the four standard tiers (`very_high`, `high`, `medium`, `low`) consistent across jurisdictions so they can be compared.
- For very large jurisdictions (federal governments, California), you may want to shift the boundaries up by an order of magnitude. Document the change.
- Use a single color family (blues by default) so the tiers read as a gradient rather than as categories.

## impact_categories

Defines the buckets for characterizing a service's economic or social impact.

```json
"impact_categories": {
  "direct_economic": { "label": "Direct economic", "color": "#2e7d32" },
  "workforce":       { "label": "Workforce", "color": "#1565c0" },
  "cost_avoidance":  { "label": "Cost avoidance", "color": "#e65100" },
  "social_roi":      { "label": "Social ROI", "color": "#6a1b9a" }
}
```

**What each category means:**

| Category | Description | Example |
|----------|-------------|---------|
| `direct_economic` | Services that directly enable revenue, trade, or economic activity. | Export permits, business registration, trade corridor infrastructure. |
| `workforce` | Services that develop human capital or help people find work. | Student aid, apprenticeship support, employment services. |
| `cost_avoidance` | Services that prevent larger downstream costs to government or society. | Child abuse reporting, preventive health, early intervention. |
| `social_roi` | Services whose primary return is social well-being rather than dollars. | Family violence support, victim services, accessibility supports. |

**Guidelines:**
- Keep the four standard categories consistent across jurisdictions.
- A service should usually have exactly one category. If it genuinely spans two, pick the dominant one.
- The `note` field on each supporting service's `economic_impact` is where the nuance lives — the category is just the bucket.

## Example: Adapting config.json for a new jurisdiction

Starting from Alberta's config, here's what you'd change for British Columbia:

```json
{
  "jurisdiction": "bc",
  "jurisdiction_name": "Province of British Columbia",
  "jurisdiction_short": "BC",
  "jurisdiction_type": "province",
  "country": "CA",
  "brand_color": "#003366",
  "brand_color_light": "#d6e2ec",
  "accent_color": "#fcba19",
  "last_updated": "2026-04",
  "legislation_source": "https://www.bclaws.gov.bc.ca/civix/document/id/complete/statreg/",
  "mandate_source_type": "mandate_letter",
  "org_unit_label": "Ministry",
  "goal_label": "Strategic Priority",
  "main_service_label": "Main Service",
  "channel_types": { /* copy Alberta's unchanged, or add BC-specific ones */ },
  "reach_tiers": { /* copy Alberta's unchanged */ },
  "impact_categories": { /* copy Alberta's unchanged */ }
}
```

The main differences for BC:
- Brand colors from the BC visual identity guide (navy + gold)
- `legislation_source` pointing to BC Laws
- `goal_label` changed to "Strategic Priority" if that's BC's term in their service plans
- Everything else stays the same — that's the whole point of externalizing these values

## Validation

After creating a config.json, verify:

1. `jurisdiction` matches the folder name exactly
2. All channel_types have `label`, `bg`, `fg`, and `digital`
3. All reach_tiers have `label` and `color`
4. All impact_categories have `label` and `color`
5. Brand colors are valid hex codes
6. `last_updated` is a valid YYYY-MM string
