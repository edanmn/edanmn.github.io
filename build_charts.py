#!/usr/bin/env python3
"""Generate the charts for the audit page from the EDAN dataset.
Reads ../data/*, writes docs/charts/*.html. The charts are drawn by docs/js/charts.js from the
description each write_chart call passes in; see edan_charts.py."""
import csv, json, os
from collections import defaultdict
from urllib.request import urlopen
from edan_charts import write_chart, county_paths

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

rows = list(csv.DictReader(open(os.path.join(DATA, "audit_full.csv"))))
def f(x):
    try: return float(x)
    except: return None

# ---------- 1. Plan rate by locale ----------
order = ["City", "Suburb", "Town", "Rural"]
by = defaultdict(lambda: [0, 0])
for r in rows:
    by[r["locale"]][1] += 1
    if r["seizure_specific"] == "1": by[r["locale"]][0] += 1
rate = [round(100 * by[l][0] / by[l][1]) for l in order]
ns = [by[l][1] for l in order]
write_chart("gap_by_locale.html", {
    "type": "columns", "title": "Public seizure plan, by district type",
    "yTitle": "% of districts with a public seizure plan", "ymax": 100,
    "cols": [{"label": l, "value": r, "text": f"{r}%", "sub": f"n={n}",
              "tip": [[f"{r}%", "of districts post a public seizure plan"], [n, "districts"]]}
             for l, r, n in zip(order, rate, ns)]})

# ---------- 2. Classification breakdown ----------
LAB = {"FOUND_SEIZURE_SPECIFIC": ("Seizure plan posted", "good"),
       "FOUND_MED_POLICY_ONLY": ("Medication policy only (no seizure mention)", "warn"),
       "NOT_FOUND": ("Nothing relevant found online", "bad"),
       "NOT_VERIFIABLE": ("Could not check", "none")}
cnt = defaultdict(int)
for r in rows: cnt[r["classification"]] += 1
keys = [k for k in LAB if k in cnt]
write_chart("classification_breakdown.html", {
    "type": "bars", "title": "What Minnesota districts actually post",
    "axis": f"Number of districts (of {len(rows)})",
    "rows": [{"label": LAB[k][0], "value": cnt[k], "text": f"{cnt[k]} ({round(100*cnt[k]/len(rows))}%)", "tone": LAB[k][1],
              "tip": [[cnt[k], "districts"], [f"{round(100*cnt[k]/len(rows))}%", f"of all {len(rows)}"]]}
             for k in keys]})

# ---------- 3. Size effect: plan rate by enrollment bucket ----------
buckets = [("Under 500", 0, 500), ("500-999", 500, 1000), ("1,000-2,499", 1000, 2500),
           ("2,500-9,999", 2500, 10000), ("10,000+", 10000, 10**9)]
bdata = {b[0]: [0, 0] for b in buckets}
for r in rows:
    e = f(r["enrollment"])
    if e is None: continue
    for name, lo, hi in buckets:
        if lo <= e < hi:
            bdata[name][1] += 1
            if r["seizure_specific"] == "1": bdata[name][0] += 1
            break
labels = [b[0] for b in buckets]
brate = [round(100 * bdata[l][0] / bdata[l][1]) if bdata[l][1] else 0 for l in labels]
bn = [bdata[l][1] for l in labels]
write_chart("size_effect.html", {
    "type": "columns", "title": "The real driver is size: plan rate rises with enrollment",
    "yTitle": "% of districts with a public seizure plan", "ymax": 100, "axis": "District enrollment",
    "cols": [{"label": l, "value": r, "text": f"{r}%", "sub": f"n={n}",
              "tip": [[f"{r}%", "of districts post a public seizure plan"], [n, "districts"]]}
             for l, r, n in zip(labels, brate, bn)]})

# ---------- 4. County map ----------
ctyfips = {}
for r in csv.DictReader(open(os.path.join(DATA, "cdc_places_mn_county_health.csv"))):
    ctyfips[r["locationname"].upper()] = r["locationid"]
cagg = defaultdict(lambda: [0, 0])
for r in rows:
    c = (r["county"] or "").upper().replace(" COUNTY", "").strip()
    cagg[c][1] += 1
    if r["seizure_specific"] == "1": cagg[c][0] += 1
with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as fh:
    counties = json.load(fh)
# The file holds every US county. Keep Minnesota's 87 (FIPS 27xxx).
counties["features"] = [ft for ft in counties["features"] if ft["id"].startswith("27")]
paths, height = county_paths(counties)
write_chart("gap_map.html", {
    "type": "counties", "title": "% of districts with NO public seizure plan, by county",
    "legend": "Districts with no public seizure plan", "valueLabel": "of districts post no plan",
    "bins": [20, 40, 60, 80], "h": height,
    "areas": [{"name": f"{c.title()} County", "d": paths[ctyfips[c]], "v": round(100 * (1 - has / tot)), "n": tot}
              for c, (has, tot) in cagg.items() if c in ctyfips and tot],
    "head": ["County", "No public plan", "Districts"]})

# ---------- 5. County need vs gap ----------
pivot = {r["County"].upper(): r for r in csv.DictReader(open(os.path.join(DATA, "cdc_places_mn_county_pivot.csv")))}
xs, ys, sizes, names = [], [], [], []
for c, (has, tot) in cagg.items():
    p = pivot.get(c)
    if p and tot:
        d = f(p["AnyDisability"])
        if d is None: continue
        xs.append(d); ys.append(round(100 * (1 - has / tot))); sizes.append(tot); names.append(c.title())
write_chart("county_need_vs_gap.html", {
    "type": "bubbles", "title": "Higher-need counties tend to have bigger gaps",
    "xTitle": "County adult disability rate (%), a need proxy", "yTitle": "% of districts with no public plan", "ymax": 100,
    "note": "A larger bubble means more districts in the county.",
    "tip": ["adult disability rate", "of districts post no plan", "districts"],
    "pts": [{"name": n, "x": x, "y": y, "n": s} for n, x, y, s in zip(names, xs, ys, sizes)],
    "head": ["County", "Adult disability rate", "No public plan", "Districts"]})

print("\nAll audit charts written.")
