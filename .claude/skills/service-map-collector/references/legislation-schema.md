# Legislation Cross-Reference Schema — {prefix}_legislation.json

## Top-level fields

```json
{
  "prefix": "cfs",
  "name": "Children and Family Services",
  "short_name": "Children & Family Services",
  "goals": [],    // Simplified goal list for the legend (see below)
  "acts": [],     // Array of Act objects (see below)
  "stats": {
    "acts_count": 8,
    "sections_count": 18,
    "services_with_leg_count": 14,
    "services_multi_act_count": 7
  }
}
```

## Simplified goal (for legend)

These are lightweight copies of the goals from the ministry JSON, used to color-code the legislation page.

```json
{
  "number": 1,
  "color": "#0070c0",
  "short_name": "Services and supports are accessible and responsive",
  "legend_label": "Addressing needs",
  "main_services": [
    {
      "number": 1,
      "name": "Report and respond to child safety concerns"
    }
  ]
}
```

## Act object

```json
{
  "abbrev": "CYFEA",
  "full_name": "Child, Youth and Family Enhancement Act",
  "color": "#0070c0",
  "citation": "RSA 2000, c C-12",
  "summary": "One paragraph summarizing what the act does and why it exists.",
  "full_text": "<HTML string with anchor spans>",
  "sections": []
}
```

### full_text format

The full_text field contains the complete text of the act as an HTML string. Anchor spans are injected before each referenced section so the legislation drawer can scroll to the right location:

```html
<span id=\"anchor-cyfea-s2\"></span>\nInterpretation\n2(1) In this Act...
```

Anchor ID format: `anchor-{abbrev_lowercase}-{section_ref}`
- Section ref is the `ref` field from the section object, lowercased: "s.2" → "s2", "Part 3" → "part-3"

If full_text is not yet available, set it to `""` (empty string) and flag it for later collection.

## Section object

```json
{
  "ref": "s.2",
  "title": "Interpretation",
  "description": "Defines key terms including what constitutes a child in need of intervention.",
  "anchor_id": "anchor-cyfea-s2",
  "services": [
    {
      "name": "Report concerns about child abuse or neglect",
      "type": "supporting",
      "goal_number": 1,
      "goal_color": "#0070c0",
      "ms_number": 1,
      "ms_name": "Report and respond to child safety concerns"
    }
  ]
}
```

## Consistency rules

1. Every service referenced in a section's `services[]` must exist as a supporting service in the ministry JSON
2. Every legislation entry on a supporting service in the ministry JSON must have a corresponding act in the legislation JSON
3. The `goal_number`, `goal_color`, `ms_number`, and `ms_name` fields on service references must match the ministry JSON exactly
4. Act abbreviations and colors must be consistent between both files
