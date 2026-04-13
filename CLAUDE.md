# GoA Service Maps

A static site that visualizes how Alberta government ministries deliver services to the public. Each ministry has a service map (goals, main services, supporting services, channels) and a legislation cross-reference page.

## Project Structure

```
goa-service-maps/
├── index.html              # Ministry listing page (home)
├── css/style.css           # All styles (single file)
├── data/                   # Ministry data (JSON, source of truth)
│   ├── ministries.json     # Index of all ministries
│   ├── tec.json            # Transportation & Economic Corridors
│   ├── tec_legislation.json
│   ├── alss.json           # Assisted Living & Social Services
│   └── alss_legislation.json
├── tec/                    # TEC ministry pages
│   ├── service-map.html    # Service map visualization
│   └── legislation.html    # Legislation cross-reference
├── alss/                   # ALSS ministry pages
│   ├── service-map.html
│   └── legislation.html
├── build.py                # Utility: generates data/ from seed data
├── netlify.toml            # Netlify redirects and headers
└── BUILD_OUTPUT.txt        # Build log reference
```

## How It Works

- Pure HTML/CSS/JS with no build step or framework
- All JS is inline in the HTML files (no external JS files)
- Each ministry page fetches its JSON data at runtime via `fetch()`
- `css/style.css` is shared across all pages
- Netlify auto-deploys on push to `main`

## Data Format

### ministries.json

Index file listing all ministries. Each entry has:

```json
{
  "prefix": "tec",
  "name": "Transportation and Economic Corridors",
  "short_name": "Transportation & Economic Corridors",
  "blurb": "Plans, builds, operates..."
}
```

The `prefix` is the key identifier. It maps to the folder name (`tec/`) and data file (`data/tec.json`).

### Ministry Data ({prefix}.json)

Hierarchical structure: Ministry > Goals > Main Services > Supporting Services

```
Ministry
├── prefix, full_name, short_name, blurb, nav_name
├── has_registry_agents (boolean)
├── foundational_services[] (ministry-level)
├── goals[]
│   ├── number, color, title, short_name, legend_label, description
│   ├── foundational_services[] (goal-level)
│   └── main_services[]
│       ├── number, name
│       ├── foundational_services[] (service-level)
│       └── supporting[]
│           ├── name, desc, users
│           ├── user_groups[] (e.g., "Individuals", "Seniors")
│           ├── channels[]
│           │   ├── type (e.g., "ch-transact", "ch-phone", "ch-inperson")
│           │   ├── label
│           │   └── url (nullable)
│           ├── legislation[]
│           │   ├── abbrev, color, full_name
│           └── mandate_tags[]
├── channel_filters[] (computed by build.py)
├── user_group_filters[] (computed by build.py)
├── channel_types {} (metadata for rendering)
└── digital_channels[] (list of digital channel type codes)
```

### Channel Types

| Code        | Label              | Type        |
| ----------- | ------------------ | ----------- |
| ch-transact | Online transaction | Digital     |
| ch-apply    | Apply              | Digital     |
| ch-check    | Check / portal     | Digital     |
| ch-find     | Find / search      | Digital     |
| ch-app      | Mobile app         | Digital     |
| ch-engage   | Engage             | Digital     |
| ch-web      | Website            | Digital     |
| ch-email    | Email              | Digital     |
| ch-phone    | Phone              | Non-digital |
| ch-mail     | Mail               | Non-digital |
| ch-inperson | In person          | Non-digital |
| ch-registry | Registry agent     | Non-digital |
| ch-pdf      | PDF / form         | Non-digital |
| ch-pub      | Publication        | Non-digital |

### Legislation Data ({prefix}\_legislation.json)

Cross-reference between legislation (acts/sections) and services:

```
├── prefix, name, short_name
├── goals[] (simplified: number, color, short_name, legend_label, main_services[])
├── acts[]
│   ├── abbrev, full_name, color, citation, summary, full_text
│   └── sections[]
│       ├── ref, title, description, anchor_id
│       └── services[] (name, type, goal_number, goal_color, ms_number, ms_name)
└── stats (acts_count, sections_count, services_with_leg_count, services_multi_act_count)
```

## Adding a New Ministry

1. Create `data/{prefix}.json` following the structure above
2. Optionally create `data/{prefix}_legislation.json`
3. Add the ministry to `data/ministries.json`
4. Create `{prefix}/service-map.html` (copy from an existing ministry, update the page)
5. Optionally create `{prefix}/legislation.html`
6. Add redirect rules to `netlify.toml` for the new prefix
7. **Review every service name** (foundational, main, and supporting) to ensure none include the name of an agency or program. Service names describe what the service does for the user. Agencies and programs are delivery mechanisms — they belong in descriptions, channels, or legislation references, not in the service title. For example: "Coordinate provincial sport policy and funding" not "Oversee Alberta Sport Connection"; "Apply for community recreation facility capital funding" not "Apply for Community Recreation Centre Infrastructure Program funding".
8. Push to `main` to deploy

## Branch Strategy

- **Data changes** (new/updated JSON in `data/`): push straight to `main`
- **Code changes** (HTML, CSS, JS, config): create a PR for review

## Running Locally

No build step. From the repo root:

```bash
npm start
```

This runs `serve` on port 8000 with clean URL support, so links like `/fp/service-map` work the same way they do on Netlify. Open `http://localhost:8000`.

## Workflow Rules

- **Do not change the developer's local tooling, server commands, or workflow without explicit approval.** If a new tool or process is needed, explain why and get confirmation before suggesting it.
- When in doubt, match existing patterns. Copy what works before inventing something new.
- **Web research:** Use the Chrome browser connection (Claude in Chrome / Control Chrome MCP tools) for all web research instead of the sandbox WebSearch/WebFetch tools. The Chrome connection can actually visit and read alberta.ca and other government sites that the sandbox tools cannot reliably reach.

## build.py

A Python utility that generates the `data/` JSON files from seed data. The seed data lives outside this repo (in Paul's service-map project). You don't need to run this for normal development. The `data/` files in this repo are the output and source of truth.

## Related

- **Paul's working copy:** 2asku.com (DreamHost, includes PHP admin panel for editing data)
- **Admin panel:** Not in this repo. Paul hosts it separately on DreamHost for editing ministry data through a web UI.
