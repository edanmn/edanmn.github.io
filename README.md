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
  data/                        Data and Methods page
  charts/                      the interactive charts, embedded in pages as iframes
  sims/distance-lookup/        distance-to-care lookup
  sims/cap-calculator/         what a $25 cap would change, the twelve most-enrolled individual plans by the twenty most prescribed medicines and five costly brands
  sims/district-compare/       one district beside similar districts
  sims/death-certificates/     death certificate counts, seven views
  packet/                      the Seizure-Safe Schools packet (PDF)
  css/extra.css                site styling (and the @font-face rules for fonts/)
  fonts/                       Inter and Newsreader, served from the site rather than Google
  css/charts.css               the look of the charts
  js/reactbits.js              home page search, light/dark fade, swipeable phone menu
  js/charts.js                 draws the charts (no chart library)
  js/demos.js, js/demo-*.js    the three interactive pages in sims/, styled by css/demos.css
  js/embed.js                  dark mode and auto height for the embedded pages
overrides/                     theme overrides: analytics, link previews, font preloads
hooks/page_dates.py            adds "Page updated <date>" under each title, from the git history
press/                         press release and outreach kit (not part of the site)
```

## Rebuilding the lookups and charts
The lookups, the district table and the charts are generated files. The scripts read EDAN's
working data from `../data/`, which is not in this repository, so they run from the parent
project:

| Script | Writes |
|--------|--------|
| `build_district_lookup.py` | `docs/find-your-district/district_lookup.html`, `district_names.json` (the names the home page search suggests), and the reply counts on the report page. The public CSV is no longer written. |
| `build_district_table.py` | `docs/find-your-district/district_table.html` |
| `build_charts.py` | the audit charts in `docs/charts/` |
| `build_initiative_charts.py` | the initiative charts and the distance-to-care map in `docs/charts/`, and `docs/sims/distance-lookup/main.html`. That includes the Medicaid trend charts (`medicaid_rx_trend.html`, `medicaid_spending_trend.html`, 2026 marked as part of a year), `asm_brandonly_share.html`, `asm_brand_vs_generic.html` and `mortality_neighbors.html`; the last two take their numbers from `NADAC` and `NEIGHBORS` near the top of that section, so update those with each pull. |
| `build_county_table.py`, `build_legislative_table.py` | the county and legislative district tables |
| `build_demos.py` | `main.html` in `docs/sims/cap-calculator/`, `district-compare/` and `death-certificates/` (the data only; the drawing code is in `docs/js/demo-*.js`) |
| `edan_charts.py` | shared helper: `write_chart()` writes one chart page |
| `postprocess_charts.py` | adds the viewport tag and `embed.js` to the one chart still made with Plotly (`county_four_layers.html`, not used on any page) |

The charts use no chart library. Each chart page holds a short description of the chart as JSON
(`window.SPEC`), and `docs/js/charts.js` draws it with `docs/css/charts.css`. The kinds of chart
and what each needs are listed at the top of `charts.js`.

`mortality_by_year.html` and `mortality_by_age.html` are built by a script that is not in this
repository. They were converted to the new format by hand; that script needs to call
`write_chart()` too, or it will put the old Plotly versions back.

Edit the script, not the generated file, or the next rebuild will undo the change.

The chart scripts also download public shape files each time they run: US county outlines, and
the Census Bureau's Minnesota school district boundaries for the distance-to-care map.

The logo in `docs/img/brand/` is saved as a 256-colour PNG, which looks the same and is about
a seventh of the size. The four chart pictures in `docs/img/` are no longer used on any page;
the medication access and SUDEP pages now embed interactive charts instead. To shrink a PNG:

```bash
.venv/bin/python -c "from PIL import Image; import sys; p=sys.argv[1]; Image.open(p).convert('RGBA').quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).save(p, optimize=True)" docs/img/NAME.png
```

This material is informational, not legal or medical advice.
