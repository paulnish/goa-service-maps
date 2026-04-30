# GoA Service Maps

Static site visualizing how Alberta government ministries deliver services to the public. Built by Paul and Tom as part of the Government of Alberta Design System initiative.

**Live site:** https://goa-service-maps.netlify.app
**Paul's working copy:** [2asku.com](https://2asku.com)

## What's in the repo

Two layers of content sit in this repo:

1. **Per-ministry service maps** — the static site you see at the live URL. Each ministry has a JSON file in `data/ab/` and a corresponding HTML page (`{prefix}/service-map.html`) that visualises it.

2. **Jurisdiction-level service-types analysis** — derived from the ministry maps:
   - `data/ab/service_types.json` — 14 service types as `(service task × Kate Tarling intent)` clusters validated by a leverage bar. Queryable JSON consumed by the GoA Design System MCP, the using-goa-design-system skill, and future docs site service-type pages.
   - `data/ab/service_types.md` — human-readable summary of the same.
   - `analysis/service-types/` — scripts and working files that produced the analysis. See `analysis/service-types/README.md` for the full pipeline.

Schema details for both layers live in `CLAUDE.md`.

## Running Locally

No build step required. Open `index.html` in a browser, or use any static file server:

```bash
# Python
python3 -m http.server 8000

# Node
npx serve .
```

Then visit `http://localhost:8000`.

Note: Clean URLs (like `/tec/service-map`) won't work locally since they rely on Netlify redirects. Use the `.html` extension directly (e.g., `tec/service-map.html`).

## Deployment

Netlify auto-deploys on push to `main`. PR deploy previews are enabled.

## Branch Strategy

- **Data changes** (new/updated ministry JSON in `data/`) — push straight to `main`
- **Code changes** (HTML, CSS, JS) — create a PR for review

## Adding a New Ministry

1. Create `data/{prefix}.json` with the ministry data (see existing files for format)
2. Create `{prefix}/service-map.html` and optionally `{prefix}/legislation.html`
3. Add the ministry to `data/ministries.json`
4. Add redirect rules to `netlify.toml` for the new prefix
5. Push to `main`
