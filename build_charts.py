#!/usr/bin/env python3
"""Generate interactive Plotly charts for the textbook from the EDAN dataset.
Outputs self-contained HTML into textbook/docs/charts/ for iframe embedding."""
import csv, json, math, os
from collections import defaultdict
from urllib.request import urlopen
import plotly.graph_objects as go

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "docs", "charts")
os.makedirs(OUT, exist_ok=True)

RED, GREEN, AMBER, GREY = "#b3202c", "#1a9850", "#fdae61", "#999999"
LAYOUT = dict(font=dict(family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif", size=14),
              margin=dict(l=60, r=20, t=50, b=50), plot_bgcolor="white", paper_bgcolor="white")

def save(fig, name):
    fig.update_layout(**LAYOUT)
    fig.write_html(os.path.join(OUT, name), include_plotlyjs="cdn", full_html=True,
                   config={"displayModeBar": False, "responsive": True})
    print("wrote charts/" + name)

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
fig = go.Figure(go.Bar(x=order, y=rate, marker_color=GREEN,
    text=[f"{r}%<br><span style='font-size:11px'>n={n}</span>" for r, n in zip(rate, ns)],
    textposition="outside",
    hovertemplate="%{x}: %{y}% of districts post a public seizure plan<extra></extra>"))
fig.update_yaxes(range=[0, 100], title="% of districts with a public seizure plan", gridcolor="#eee")
fig.update_layout(title="Public seizure plan, by district type")
save(fig, "gap_by_locale.html")

# ---------- 2. Classification breakdown ----------
LAB = {"FOUND_SEIZURE_SPECIFIC": ("Seizure plan posted", GREEN),
       "FOUND_MED_POLICY_ONLY": ("Medication policy only (no seizure mention)", AMBER),
       "NOT_FOUND": ("Nothing relevant found online", RED),
       "NOT_VERIFIABLE": ("Could not check", GREY)}
cnt = defaultdict(int)
for r in rows: cnt[r["classification"]] += 1
keys = [k for k in LAB if k in cnt]
fig = go.Figure(go.Bar(
    y=[LAB[k][0] for k in keys][::-1], x=[cnt[k] for k in keys][::-1], orientation="h",
    marker_color=[LAB[k][1] for k in keys][::-1],
    text=[f"{cnt[k]} ({round(100*cnt[k]/len(rows))}%)" for k in keys][::-1], textposition="outside",
    hovertemplate="%{y}: %{x} districts<extra></extra>"))
fig.update_xaxes(title="Number of districts (of 328)", gridcolor="#eee", range=[0, max(cnt.values())*1.2])
fig.update_layout(title="What Minnesota districts actually post")
save(fig, "classification_breakdown.html")

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
fig = go.Figure(go.Bar(x=labels, y=brate, marker_color=RED,
    text=[f"{r}%<br><span style='font-size:11px'>n={n}</span>" for r, n in zip(brate, bn)],
    textposition="outside",
    hovertemplate="%{x} students: %{y}% post a public plan<extra></extra>"))
fig.update_yaxes(range=[0, 100], title="% of districts with a public seizure plan", gridcolor="#eee")
fig.update_xaxes(title="District enrollment")
fig.update_layout(title="The real driver is size: plan rate rises with enrollment")
save(fig, "size_effect.html")

# ---------- 4. Interactive county choropleth ----------
ctyfips = {}
for r in csv.DictReader(open(os.path.join(DATA, "cdc_places_mn_county_health.csv"))):
    ctyfips[r["locationname"].upper()] = r["locationid"]
cagg = defaultdict(lambda: [0, 0])
for r in rows:
    c = (r["county"] or "").upper().replace(" COUNTY", "").strip()
    cagg[c][1] += 1
    if r["seizure_specific"] == "1": cagg[c][0] += 1
fips, z, txt = [], [], []
for c, (has, tot) in cagg.items():
    if c in ctyfips and tot:
        fips.append(ctyfips[c]); z.append(round(100 * (1 - has / tot)))
        txt.append(f"{c.title()} County ({tot} districts)")
with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as fh:
    counties = json.load(fh)
fig = go.Figure(go.Choropleth(geojson=counties, locations=fips, z=z, text=txt,
    colorscale="Reds", zmin=0, zmax=100, marker_line_color="white", marker_line_width=0.5,
    colorbar_title="% no plan",
    hovertemplate="%{text}<br>%{z}% of districts post no plan<extra></extra>"))
fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(title="% of districts with NO public seizure plan, by county",
                  margin=dict(l=0, r=0, t=50, b=0))
fig.write_html(os.path.join(OUT, "gap_map.html"), include_plotlyjs="cdn", full_html=True,
               config={"displayModeBar": False, "responsive": True})
print("wrote charts/gap_map.html")

# ---------- 5. County need vs gap scatter ----------
pivot = {r["County"].upper(): r for r in csv.DictReader(open(os.path.join(DATA, "cdc_places_mn_county_pivot.csv")))}
xs, ys, sizes, names = [], [], [], []
for c, (has, tot) in cagg.items():
    p = pivot.get(c)
    if p and tot:
        d = f(p["AnyDisability"])
        if d is None: continue
        xs.append(d); ys.append(round(100 * (1 - has / tot))); sizes.append(tot); names.append(c.title())
fig = go.Figure(go.Scatter(x=xs, y=ys, mode="markers", text=names,
    marker=dict(size=[6 + s * 2 for s in sizes], color=ys, colorscale="Reds", cmin=0, cmax=100,
                line=dict(width=1, color="#999"), showscale=False, opacity=0.8),
    hovertemplate="%{text}<br>Adult disability: %{x}%<br>%{y}% of districts post no plan<br>(bubble size = # districts)<extra></extra>"))
fig.update_xaxes(title="County adult disability rate (%) - a need proxy", gridcolor="#eee")
fig.update_yaxes(title="% of districts with no public plan", gridcolor="#eee", range=[0, 105])
fig.update_layout(title="Higher-need counties tend to have bigger gaps")
save(fig, "county_need_vs_gap.html")

# Plotly's full_html output omits a mobile viewport tag; inject it so charts
# render responsively inside their iframes on phones.
import glob
VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'
for fp in glob.glob(os.path.join(OUT, "*.html")):
    t = open(fp, encoding="utf-8").read()
    if 'name="viewport"' not in t and "<head>" in t:
        open(fp, "w", encoding="utf-8").write(t.replace("<head>", "<head>" + VIEWPORT, 1))
print("\nAll charts written to", OUT, "(viewport injected)")
