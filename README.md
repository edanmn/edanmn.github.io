# Epilepsy Data & Advocacy Network (EDAN)

The source for <https://edanmn.org/>. EDAN is a student-led project that assembles public data
about epilepsy in Minnesota and publishes it with the method attached: a seizure-plan audit of
all 329 school districts, medication access, distance to care, and SUDEP.

The site is built with [MkDocs](https://www.mkdocs.org/) and
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

## Run it locally
```bash
python3 -m venv .venv
.venv/bin/pip install "mkdocs>=1.6,<2" "mkdocs-material>=9,<10"
.venv/bin/mkdocs serve
# open http://127.0.0.1:8000
```

## Publish
Every push to `main` runs `.github/workflows/deploy.yml`, which builds the site and deploys it
to GitHub Pages.

## Structure
```
mkdocs.yml                     site config and navigation
docs/
  index.md                     home page
  initiatives/                 the three initiatives, plus distance to care
  chapters/                    the Minnesota law, and the audit write-up
  find-your-district/          the district lookup and the full district table
  data/                        Data and Methods page, and the audit as a CSV
  charts/                      interactive Plotly charts, embedded in pages as iframes
  sims/distance-lookup/        distance-to-care lookup
  packet/                      the Seizure-Safe Schools packet (PDF)
  css/extra.css                site styling
  js/reactbits.js              page animations
  js/embed.js                  dark mode, auto height and phone layout for the embedded pages
overrides/                     theme overrides: analytics, link previews, home page sidebar
press/                         press release and outreach kit (not part of the site)
```

## Rebuilding the lookups and charts
The lookups, the district table and the charts are generated files. The scripts read EDAN's
working data from `../data/`, which is not in this repository, so they run from the parent
project:

| Script | Writes |
|--------|--------|
| `build_district_lookup.py` | `docs/find-your-district/district_lookup.html`, `docs/data/mn_seizure_plan_audit.csv`, and the reply counts on the report page |
| `build_district_table.py` | `docs/find-your-district/district_table.html` |
| `build_charts.py` | the audit charts in `docs/charts/` |
| `build_initiative_charts.py` | the initiative charts in `docs/charts/` and `docs/sims/distance-lookup/main.html` |
| `postprocess_charts.py` | adds the viewport tag and `embed.js` to every chart (the two chart scripts call it) |

Edit the script, not the generated file, or the next rebuild will undo the change.

The chart scripts also download public shape files each time they run: US county outlines, and
the Census Bureau's Minnesota school district boundaries for the distance-to-care map.

This material is informational, not legal or medical advice.
