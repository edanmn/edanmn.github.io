#!/usr/bin/env python3
"""Interactive charts and lookup tools for the initiative pages.
Reads ../data/*, writes docs/charts/*.html and docs/sims/distance-lookup/main.html. Charts are
drawn by docs/js/charts.js from the description each write_chart call passes in (see
edan_charts.py); the distance-to-care map has its own, larger page further down."""
import csv, io, json, math, os, re, zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from urllib.request import urlopen
import plotly.graph_objects as go          # only for county_four_layers.html, which no page uses yet
from edan_charts import write_chart, albers

HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "docs", "charts"); os.makedirs(OUT, exist_ok=True)
RED, GREEN, AMBER, GREY, INK = "#b3202c", "#1a9850", "#fdae61", "#999999", "#24211e"
LAYOUT = dict(font=dict(family="system-ui,-apple-system,Segoe UI,Roboto,sans-serif", size=14),
              margin=dict(l=60, r=20, t=50, b=50), plot_bgcolor="white", paper_bgcolor="white")
def save(fig, name):
    fig.update_layout(**LAYOUT)
    fig.write_html(os.path.join(OUT, name), include_plotlyjs="cdn", full_html=True, config={"displayModeBar": False, "responsive": True})
    print("wrote charts/" + name)
def f(x):
    try: return float(x)
    except: return None
def rd(name): return list(csv.DictReader(open(os.path.join(DATA, name))))

# ---------- Initiative 1: no-plan districts by English learner share ----------
lang = [r for r in rd("mn_district_language.csv") if r["classification"] and r["classification"] != "FOUND_SEIZURE_SPECIFIC" and f(r["el_share_pct"]) is not None]
lang = sorted(lang, key=lambda r: -f(r["el_share_pct"]))[:25]
write_chart("el_noplan_districts.html", {
    "type": "bars", "title": "No-plan districts with the most English learners",
    "axis": "English learners, % of enrollment (NCES 2021)",
    "rows": [{"label": r["district"].title(), "value": f(r["el_share_pct"]), "text": f'{f(r["el_share_pct"]):g}%',
              "tip": [[f'{f(r["el_share_pct"]):g}%', "English learners"], [r["english_learners_2021"], "students"],
                      [r["county"], "no findable seizure plan"]]} for r in lang],
    "head": ["District", "English learners", "Students", "County"]})

# ---------- Initiative 2: four layers, one county ----------
comp = rd("mn_district_risk_composite.csv")
cty = defaultdict(lambda: {"n": 0, "noplan": 0, "enroll": 0.0, "ems": None, "nonurse": []})
for r in comp:
    c = cty[r["county"]]; c["n"] += 1; c["enroll"] += f(r["enrollment"]) or 0
    if r["classification"] != "FOUND_SEIZURE_SPECIFIC": c["noplan"] += 1
    c["ems"] = f(r["ems_p90_min"]); 
    p = (r.get("prob_no_nurse") or "").replace("%", ""); 
    if f(p) is not None: c["nonurse"].append(f(p))
names = sorted(cty); 
fig = go.Figure(go.Scatter(x=[cty[c]["ems"] for c in names], y=[100*cty[c]["noplan"]/cty[c]["n"] for c in names], mode="markers",
    marker=dict(size=[max(8, min(40, (cty[c]["enroll"] ** 0.5) / 6)) for c in names], color=[sum(cty[c]["nonurse"])/len(cty[c]["nonurse"]) if cty[c]["nonurse"] else 0 for c in names],
                colorscale="YlOrRd", showscale=True, colorbar=dict(title="Likely no<br>school nurse, %"), line=dict(width=0.5, color=INK)),
    text=names, customdata=[[cty[c]["n"], cty[c]["noplan"], int(cty[c]["enroll"])] for c in names],
    hovertemplate="<b>%{text}</b><br>%{customdata[1]} of %{customdata[0]} districts post no seizure plan<br>Slowest 10% of ambulance calls: %{x} min<br>Students: %{customdata[2]:,}<extra></extra>"))
fig.add_vline(x=20, line_dash="dot", line_color=GREY, annotation_text="20 min", annotation_position="top")
fig.update_xaxes(title="County ambulance response, 90th percentile (minutes)", gridcolor="#eee"); fig.update_yaxes(title="% of districts with no findable seizure plan", gridcolor="#eee", range=[-5, 105])
fig.update_layout(title="Every Minnesota county: plans, ambulances, nurses, students (bubble size)", height=520)
save(fig, "county_four_layers.html")

# ---------- Initiative 3: medication by molecule, and cost per prescription ----------
yr = rd("mn_medicaid_asm_by_year.csv")
years = sorted({int(r["year"]) for r in yr if int(r["year"]) <= 2025})
tot = defaultdict(float)
for r in yr: tot[r["molecule"]] += f(r["prescriptions"]) or 0
mols = sorted(tot, key=lambda m: -tot[m])[:14]
by_mol = {m: {int(r["year"]): f(r["prescriptions"]) for r in yr if r["molecule"] == m} for m in mols}
write_chart("asm_by_molecule.html", {
    "type": "lines", "title": "Minnesota Medicaid antiseizure prescriptions by drug",
    "sub": "Press a drug's name to show or hide it.", "yTitle": "Prescriptions per year", "toggle": True,
    "x": years,
    # The six most prescribed are drawn to start with; the rest wait for a press.
    "series": [{"name": m.replace("_", " "), "values": [by_mol[m].get(y) for y in years], "on": i < 6}
               for i, m in enumerate(mols)],
    "head": ["Year"]})
c25 = [(r["molecule"], f(r["total_reimbursed_usd"]) / f(r["prescriptions"]), f(r["prescriptions"])) for r in yr if r["year"] == "2025" and f(r["prescriptions"])]
c25 = sorted(c25, key=lambda x: x[1])
LABEL = {"rescue_diazepam": "nasal diazepam (Valtoco)", "rescue_midazolam": "nasal midazolam (Nayzilam)"}  # 2025 SDUD rows are these brands only
write_chart("asm_cost_per_rx.html", {
    "type": "bars", "scale": "log", "title": "Average Minnesota Medicaid payment per prescription, by drug, 2025",
    "axis": "Average Medicaid reimbursement per prescription, 2025 (log scale)",
    "rows": [{"label": LABEL.get(m, m.replace("_", " ")), "value": round(cost), "text": f"${round(cost):,}",
              "tip": [[f"${round(cost):,}", "per prescription"], [f"{n:,.0f}", "prescriptions in 2025"]]}
             for m, cost, n in reversed(c25)],          # dearest first
    "head": ["Drug", "Per prescription", "Prescriptions in 2025"]})

# ---------- Initiative 4: map + lookup ----------
# The map is hand-built SVG rather than Plotly, so it loads fast and plain scrolling never zooms
# it. Each district's territory is shaded in one of five distance classes; child neurologist
# practices are rings, larger where more neurologists practise.
MAP_BINS = [15, 30, 60, 100]     # class edges: miles to the nearest child neurologist
MAP_NEAR_MI = 40                 # an out-of-state practice this close to Minnesota is drawn
MAP_CLUSTER_MI = 12              # practices closer together than this share one ring
MAP_TOLERANCE = 3                # how far a simplified border may stray, in tenths of a frame unit
EARTH_MI = 3958.8
# District boundaries: US Census Bureau cartographic boundary files, Minnesota (state 27).
# Unified districts, plus the handful Minnesota files as elementary districts.
CENSUS_KML = "https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_27_%s_500k.zip"

def read_kml(zipped):
    """Shapes from a Census boundary KML zip: [{"name", "polys": [[outer ring, hole, ...], ...]}]."""
    z = zipfile.ZipFile(io.BytesIO(zipped))
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    root = ET.fromstring(z.read(next(n for n in z.namelist() if n.endswith(".kml"))))
    return [{"name": pm.find(".//k:SimpleData[@name='NAME']", ns).text,
             "polys": [[[tuple(map(float, c.split(",")[:2])) for c in ring.text.split()]
                        for ring in poly.findall(".//k:coordinates", ns)]
                       for poly in pm.findall(".//k:Polygon", ns)]}
            for pm in root.findall(".//k:Placemark", ns)]

def in_ring(x, y, ring):
    inside = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside

def in_shape(lon, lat, shape):
    return any(in_ring(lon, lat, poly[0]) and not any(in_ring(lon, lat, hole) for hole in poly[1:])
               for poly in shape["polys"])

def match_shapes(districts, shapes):
    """Pair each district with its Census shape: by name where the two names agree, otherwise by
    the one unclaimed shape its office sits in. Returns {district index: shape index}."""
    norm = lambda name: re.sub(r"[^a-z0-9]", "", name.lower())
    by_name = {}
    for j, shape in enumerate(shapes):
        by_name.setdefault(norm(shape["name"]), []).append(j)
    pairs = {i: by_name[norm(r["d"])][0] for i, r in enumerate(districts) if len(by_name.get(norm(r["d"]), [])) == 1}
    claimed = set(pairs.values())
    for i, r in enumerate(districts):
        if i not in pairs:
            inside = [j for j, shape in enumerate(shapes) if j not in claimed and in_shape(r["lon"], r["lat"], shape)]
            if len(inside) == 1:
                pairs[i] = inside[0]; claimed.add(inside[0])
    return pairs

def dp(pts, tol):
    """Douglas-Peucker: drop the points of a line that stray less than tol from it."""
    keep = [False] * len(pts); keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay; den = math.hypot(dx, dy)
        far, at = tol, None
        for i in range(a + 1, b):
            px, py = pts[i]
            d = abs(dx * (py - ay) - dy * (px - ax)) / den if den else math.hypot(px - ax, py - ay)
            if d > far: far, at = d, i
        if at is not None:
            keep[at] = True; stack += [(a, at), (at, b)]
    return [p for p, kept in zip(pts, keep) if kept]

def simplify_shared(rings, tol):
    """Simplify closed rings so that a border two districts share is simplified once and stays
    shared, leaving no slivers between neighbours: cut each ring where three or more borders
    meet, and simplify the pieces."""
    nbrs = {}
    for ring in rings:
        body = ring[:-1]
        for i, pt in enumerate(body):
            nbrs.setdefault(pt, set()).update((body[i - 1], body[(i + 1) % len(body)]))
    done = {}
    def piece(pts):
        fwd = tuple(pts); key = min(fwd, fwd[::-1])
        if key not in done: done[key] = dp(list(key), tol)
        return done[key] if key == fwd else done[key][::-1]
    out = []
    for ring in rings:
        body = ring[:-1]
        cuts = [i for i, pt in enumerate(body) if len(nbrs[pt]) != 2]
        if not cuts:        # an island or a hole: start at a fixed vertex so both sides agree
            at = body.index(min(body))
            out.append(piece(body[at:] + body[:at] + [body[at]])); continue
        new = []
        for a, b in zip(cuts, cuts[1:] + [cuts[0] + len(body)]):
            new += piece([body[i % len(body)] for i in range(a, b + 1)])[:-1]
        out.append(new + [new[0]])
    return out

def centroid(ring):
    """Centre of a closed ring, and its area."""
    a = cx = cy = 0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        w = x1 * y2 - x2 * y1; a += w; cx += (x1 + x2) * w; cy += (y1 + y2) * w
    return (cx / (3 * a), cy / (3 * a), abs(a) / 2) if a else (ring[0][0], ring[0][1], 0)

def care_map_data(districts, providers, counties, shapes):
    """Project the state, the district shapes and the practices into one frame 1000 units wide."""
    rings = []
    for ft in counties["features"]:
        g = ft["geometry"]
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            rings += [[albers(lon, lat) for lon, lat in ring] for ring in poly]
    border = [pt for ring in rings for pt in ring]
    x0, y1 = min(x for x, _ in border), max(y for _, y in border)
    k = 1000 / (max(x for x, _ in border) - x0)
    place = lambda x, y: (round((x - x0) * k, 1), round((y1 - y) * k, 1))
    path = "".join("M" + "L".join("%g,%g" % place(x, y) for x, y in ring) + "Z" for ring in rings)

    # District shapes, in whole tenths of a frame unit so that paths are short and a vertex two
    # districts share is exactly the same point in both.
    tenths = lambda lon, lat: tuple(round(v * 10) for v in place(*albers(lon, lat)))
    def ring_of(ring):
        pts = [tenths(lon, lat) for lon, lat in ring]
        pts = [p for i, p in enumerate(pts) if i == 0 or p != pts[i - 1]]
        return pts if len(pts) >= 4 and pts[0] == pts[-1] else None
    where, flat = [], []                       # where[n] = (shape, polygon) of the n-th ring in flat
    for j, shape in enumerate(shapes):
        for q, poly in enumerate(shape["polys"]):
            for ring in poly:
                if ring_of(ring): where.append((j, q)); flat.append(ring_of(ring))
    outline = {}                               # shape -> polygon -> its simplified rings, outer first
    for (j, q), ring in zip(where, simplify_shared(flat, MAP_TOLERANCE)):
        if len(ring) >= 4: outline.setdefault(j, {}).setdefault(q, []).append(ring)

    pairs = match_shapes(districts, shapes)
    missing = [r["d"] for i, r in enumerate(districts) if i not in pairs]
    if missing: print("WARNING: no boundary shape for", missing)
    pts = []
    for i, r in enumerate(districts):
        p = {"d": r["d"], "c": r["c"], "k": sum(float(r["cn"]) > b for b in MAP_BINS),
             "cn": r["cn"], "ep": r["ep"], "na": r["na"], "ph": r["ph"], "ems": r["ems"], "plan": r["plan"]}
        polys = list(outline.get(pairs.get(i), {}).values())
        if polys:
            p["g"] = "".join("M%d,%d" % ring[0] + "l" + " ".join("%d,%d" % (x - px, y - py) for (px, py), (x, y) in zip(ring, ring[1:-1])) + "z"
                             for poly in polys for ring in poly)
            # The name goes at the centre of the district's largest piece, or at its office when
            # that centre falls outside the shape.
            main = max((poly[0] for poly in polys), key=lambda ring: centroid(ring)[2])
            cx, cy, _ = centroid(main)
            if not in_ring(cx, cy, main): cx, cy = tenths(r["lon"], r["lat"])
            p["x"], p["y"] = round(cx / 10, 1), round(cy / 10, 1)
            p["w"] = (max(x for x, _ in main) - min(x for x, _ in main)) / 10
            every = [pt for poly in polys for pt in poly[0]]
            p["b"] = [min(x for x, _ in every) / 10, min(y for _, y in every) / 10,
                      max(x for x, _ in every) / 10, max(y for _, y in every) / 10]
        pts.append(p)
    pts.sort(key=lambda p: float(p["cn"]))

    # One entry per city, then merge cities that would sit on top of each other at this scale.
    cities = {}
    for r in providers:
        cities.setdefault(r["city"], []).append(albers(r["lon"], r["lat"]))
    cities = [{"city": name, "n": len(xy), "x": sum(x for x, _ in xy) / len(xy), "y": sum(y for _, y in xy) / len(xy)}
              for name, xy in cities.items()]
    miles = lambda a, b: math.hypot(a["x"] - b["x"], a["y"] - b["y"]) * EARTH_MI
    groups = []
    for c in sorted(cities, key=lambda c: (-c["n"], c["city"])):
        near = [g for g in groups if any(miles(c, m) < MAP_CLUSTER_MI for m in g)]
        groups = [g for g in groups if not any(g is h for h in near)] + [[c] + [m for g in near for m in g]]
    sites, off = [], []
    for g in groups:
        g.sort(key=lambda m: (-m["n"], m["city"]))
        n = sum(m["n"] for m in g)
        name = "Twin Cities" if {"Minneapolis", "Saint Paul"} <= {m["city"] for m in g} else g[0]["city"]
        x, y = sum(m["x"] * m["n"] for m in g) / n, sum(m["y"] * m["n"] for m in g) / n
        if min(math.hypot(x - bx, y - by) for bx, by in border) * EARTH_MI < MAP_NEAR_MI:
            px, py = place(x, y)
            sites.append({"n": name, "k": n, "x": px, "y": py,
                          "m": ", ".join(f'{m["city"]} {m["n"]}' for m in g) if len(g) > 1 else ""})
            if len(g) > 1:      # zoomed in, the cluster is drawn as its separate cities
                sites[-1]["parts"] = [{"n": m["city"], "k": m["n"], **dict(zip("xy", place(m["x"], m["y"])))} for m in g]
        else:
            off.append((n, name))
    sites.sort(key=lambda s: (-s["k"], s["n"]))
    return {"bins": MAP_BINS, "h": place(x0, min(y for _, y in border))[1], "path": path, "P": pts, "S": sites,
            "off": [f"{name} ({n})" for n, name in sorted(off, key=lambda o: (-o[0], o[1]))]}

acc = rd("mn_district_care_access.csv")
prov = [r for r in rd("mn_epilepsy_providers.csv") if r["is_child_neurology"] == "True" and r["lat"]]
districts = [{"d": r["district"].title(), "c": r["county"], "lon": f(r["lon"]), "lat": f(r["lat"]),
              "cn": r["nearest_child_neurology_miles"], "ep": r["nearest_epilepsy_miles"],
              "na": r["nearest_naec_center_miles"], "ph": r.get("nearest_pharmacy_miles", ""), "ems": r["ems_p90_min"],
              "plan": "yes" if r["classification"] == "FOUND_SEIZURE_SPECIFIC" else "no"} for r in acc]
providers = [{"city": r["city"].title(), "lon": f(r["lon"]), "lat": f(r["lat"])} for r in prov]
with urlopen("https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json") as fh:
    counties = json.load(fh)
counties["features"] = [ft for ft in counties["features"] if ft["id"].startswith("27")]   # Minnesota only
shapes = []
for kind in ("unsd", "elsd"):
    with urlopen(CENSUS_KML % kind) as fh:
        shapes += read_kml(fh.read())

CARE_MAP_HTML = """<!doctype html>
<html lang="en" data-autoheight><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Distance to care map</title>
<style>
 /* District shades are one red ramp, near to far. Each mode has its own steps, checked for
    even lightness steps; in dark mode the ramp runs the other way, so "near" still recedes. */
 :root{
  --bg:#fcfcfb;--fg:#232020;--muted:#5d5851;--line:#e6e2db;
  --land:#f1eeea;--state:#a9a399;--edge:rgba(70,20,20,.3);--ring:#1f4e9c;
  --tip:#fff;--tipline:rgba(0,0,0,.14);
  --s0:#fed2ce;--s1:#f3aca6;--s2:#e47c76;--s3:#c64545;--s4:#8d1920;
 }
 [data-theme=dark]{
  --bg:#16140f;--fg:#e6e1d9;--muted:#aaa39a;--line:#3a352e;
  --land:#211e18;--state:#6b655c;--edge:rgba(255,235,230,.25);--ring:#8ab4ff;
  --tip:#26221c;--tipline:rgba(255,255,255,.16);
  --s0:#462624;--s1:#773734;--s2:#b04947;--s3:#e56965;--s4:#fba7a1;
 }
 *{box-sizing:border-box}
 body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:16px;color:var(--fg);background:var(--bg);line-height:1.45}
 h1{font-size:1rem;font-weight:650;margin:0 0 2px}
 .sub{color:var(--muted);font-size:.84rem;margin:0 0 12px}
 .fig{display:grid;grid-template-columns:minmax(0,1fr) 200px;gap:20px;align-items:start}
 .map{position:relative;min-width:0}
 canvas{display:block;width:100%}
 svg{position:absolute;inset:0;display:block;width:100%;touch-action:pan-y;user-select:none;-webkit-user-select:none}
 .zoomed canvas{border-radius:8px;box-shadow:0 0 0 1px var(--line)}
 .zoomed svg{touch-action:none;cursor:grab}
 .dragging svg{cursor:grabbing}
 .halo{fill:none;stroke:var(--bg);stroke-width:5}
 .site{fill:none;stroke:var(--ring);stroke-width:2}
 .lab{font-size:12px;font-weight:600;fill:var(--fg);paint-order:stroke;stroke:var(--bg);stroke-width:3.5px;stroke-linejoin:round}
 .name{font-size:11px;fill:var(--fg);text-anchor:middle;paint-order:stroke;stroke:var(--bg);stroke-width:3px;stroke-linejoin:round}
 .hit{fill:none;stroke:var(--fg);stroke-width:2;stroke-linejoin:round;vector-effect:non-scaling-stroke;display:none}
 .pick{fill:none;stroke:var(--ring);stroke-width:3;stroke-linejoin:round;vector-effect:non-scaling-stroke;display:none}   /* the district picked in the lookup */
 /* The hover card grows out of the pointer and fades away, rather than blinking on and off. */
 .tip{position:absolute;left:0;top:0;visibility:hidden;opacity:0;transform:scale(.96);transition:opacity .1s ease-out,transform .16s cubic-bezier(.2,.8,.2,1),visibility 0s .1s;pointer-events:none;z-index:2;width:max-content;max-width:min(310px,94%);padding:10px 12px;border-radius:8px;background:color-mix(in srgb,var(--tip) 86%,transparent);-webkit-backdrop-filter:blur(16px) saturate(170%);backdrop-filter:blur(16px) saturate(170%);border:1px solid var(--tipline);box-shadow:0 4px 16px rgba(0,0,0,.16);font-size:.8rem}
 .tip.on{visibility:visible;opacity:1;transform:none;transition-delay:0s}
 .tip b{display:block;font-size:.86rem}
 .tip .where{display:block;color:var(--muted);margin-bottom:6px}
 .tip dl{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;margin:0}
 .tip dt{font-weight:650;text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
 .tip dd{margin:0;color:var(--muted)}
 .key h2{font-size:.8rem;font-weight:650;margin:0 0 6px}
 .key ul{list-style:none;margin:0 0 14px;padding:0;font-size:.82rem}
 .key li{display:flex;align-items:center;gap:8px;padding:2px 0}
 .key .n{color:var(--muted);margin-left:auto;font-variant-numeric:tabular-nums}
 .sw{flex:none;width:13px;height:13px;border-radius:3px;box-shadow:inset 0 0 0 1px var(--edge)}
 .sw.k0{background:var(--s0)}.sw.k1{background:var(--s1)}.sw.k2{background:var(--s2)}.sw.k3{background:var(--s3)}.sw.k4{background:var(--s4)}
 .sw.ring{border:2px solid var(--ring);border-radius:50%;box-shadow:none}
 .note{color:var(--muted);font-size:.78rem;margin:0 0 10px}
 button{font:inherit;font-size:.82rem;padding:6px 11px;border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--fg);cursor:pointer;transition:transform .1s ease-out}
 button:hover{border-color:var(--muted)}
 button:active{transform:scale(.95)}                 /* answer the press itself, not the release */
 button:disabled{opacity:.4;cursor:default;transform:none}
 .zoom{position:absolute;top:0;right:0;z-index:1;display:flex;flex-direction:column;align-items:flex-end;gap:4px}
 /* The controls and the hover card float over the map as a frosted layer. */
 .zoom button{width:32px;height:32px;padding:0;font-size:1.15rem;line-height:1;background:color-mix(in srgb,var(--bg) 70%,transparent);-webkit-backdrop-filter:blur(12px) saturate(170%);backdrop-filter:blur(12px) saturate(170%)}
 .zoom #zreset{width:auto;height:26px;padding:0 8px;font-size:.72rem}
 @media (prefers-reduced-transparency:reduce){.zoom button,.tip{background:var(--bg);-webkit-backdrop-filter:none;backdrop-filter:none}}
 @media (prefers-contrast:more){.zoom button,.tip{background:var(--bg);border-color:var(--fg);-webkit-backdrop-filter:none;backdrop-filter:none}}
 @media (prefers-reduced-motion:reduce){button{transition:none}button:active{transform:none}.tip{transition:none;transform:none}}
 .map:focus-visible{outline:3px solid var(--ring);outline-offset:3px;border-radius:8px}
 .tablewrap{display:none;margin-top:14px;max-height:420px;overflow:auto;border:1px solid var(--line);border-radius:8px}
 table{border-collapse:collapse;width:100%;font-size:.8rem}
 caption{text-align:left;padding:8px;color:var(--muted)}
 th,td{text-align:left;padding:5px 8px;border-bottom:1px solid var(--line);white-space:nowrap}
 th{position:sticky;top:0;background:var(--bg);font-weight:650}
 .num{text-align:right;font-variant-numeric:tabular-nums}
 @media(max-width:640px){body{padding:12px}.fig{grid-template-columns:1fr;gap:12px}}
</style></head><body>
<h1>Distance from each school district to the nearest child neurologist</h1>
<p class="sub">Each district is shaded by how far its office is from the nearest child neurologist. Hover or tap a district for its distances. Zoom in with the buttons, a pinch, or Ctrl + scroll, then drag to move around.</p>
<div class="fig">
 <div class="map" id="map" tabindex="0" role="group" aria-label="Map. With the keyboard: plus and minus zoom, zero resets, and the arrow keys move the map once it is zoomed in.">
  <canvas id="cv"></canvas>
  <svg id="svg" role="img" aria-labelledby="alt"><title id="alt"></title>
   <g id="over"><path class="pick" id="pick"/><path class="hit" id="hitr"/></g>
   <g id="names"></g><g id="sites"></g><circle class="hit" id="hit"/>
  </svg>
  <div class="zoom" role="group" aria-label="Zoom the map">
   <button type="button" id="zin" aria-label="Zoom in">+</button>
   <button type="button" id="zout" aria-label="Zoom out">&minus;</button>
   <button type="button" id="zreset">Reset</button>
  </div>
  <div class="tip" id="tip" role="status"></div>
 </div>
 <div class="key">
  <h2>Miles from the district office to the nearest child neurologist</h2>
  <ul id="classes"></ul>
  <ul><li><span class="sw ring"></span>Child neurologist practice. A larger ring means more neurologists.</li></ul>
  <p class="note" id="off"></p>
  <p class="note">Straight-line miles from the district office, so the drive is longer. The shade describes the office, not every home in the district.</p>
  <p class="note">Sources: NPPES, NCES, MN OEMS, EDAN audit. District boundaries: US Census Bureau, 2024.</p>
  <button type="button" id="toggle" aria-expanded="false" aria-controls="tablewrap">Show as a table</button>
 </div>
</div>
<div class="tablewrap" id="tablewrap" tabindex="0"></div>

<script>
// M.path: Minnesota's counties as one SVG path, 1000 units wide and M.h tall; only its outer
// edge is drawn, as the state outline.
// M.P: districts. g is the district's shape as an SVG path in tenths of a unit, b its bounding
// box and (x, y) the point its name is centred on, in units; k is the distance class.
// M.S: practices drawn on the map; a cluster of nearby cities also carries them one by one in "parts".
const M = __MAP__;
const NS = "http://www.w3.org/2000/svg";
const $ = (id) => document.getElementById(id);
const svg = $("svg"), cv = $("cv"), ctx = cv.getContext("2d"), map = $("map"), tip = $("tip");
function el(name, attrs, parent){
 const e = document.createElementNS(NS, name);
 for (const a in attrs) e.setAttribute(a, attrs[a]);
 parent.appendChild(e); return e;
}
function html(name, text, cls){
 const e = document.createElement(name); e.textContent = text; if (cls) e.className = cls; return e;
}

const top2 = M.bins[M.bins.length - 2];
$("alt").textContent = `Map of Minnesota's ${M.P.length} school districts, each shaded by straight-line miles from its office to the nearest child neurologist. ${M.P.filter(p => p.k >= M.bins.length - 1).length} districts are more than ${top2} miles away. The table below the map has every district.`;

// ---- Key: the five distance classes, with how many districts fall in each ----
const LABELS = M.bins.map((b, i) => i ? `${M.bins[i - 1]} to ${b}` : `${b} or less`).concat(`More than ${M.bins[M.bins.length - 1]}`);
LABELS.forEach((label, i) => {
 const li = document.createElement("li");
 li.append(html("span", "", "sw k" + i), label, html("span", String(M.P.filter(p => p.k === i).length), "n"));
 $("classes").appendChild(li);
});
if (M.off.length) $("off").textContent = "Counted in the distances but off this map: " + M.off.join(", ") + ".";

// ---- Marks ----
// Districts are painted on a canvas: tens of thousands of border points redraw in a few
// milliseconds there, which keeps zooming and dragging smooth. Rings and names sit in the SVG on top.
const state = new Path2D(M.path);
const shapes = M.P.map(p => p.g ? new Path2D(p.g) : null);
// One path per distance class and one for every border, so a redraw is six draw calls, not 658.
const fills = LABELS.map(() => new Path2D()), borders = new Path2D();
shapes.forEach((shape, i) => { if (shape) { fills[M.P[i].k].addPath(shape); borders.addPath(shape); } });
// Every ring that can be drawn. A cluster such as the Twin Cities is one ring from afar and
// its separate cities once the map is zoomed in.
const marks = [];
M.S.forEach(s => {
 marks.push({s, when: s.parts ? "far" : "always"});
 (s.parts || []).forEach(p => marks.push({s: p, when: "near"}));
});
marks.forEach(m => {
 m.halo = el("circle", {class: "halo"}, $("sites")); m.ring = el("circle", {class: "site"}, $("sites"));
 m.lab = el("text", {class: "lab"}, $("sites")); m.lab.textContent = m.s.n;
});
const siteR = (s) => 5 + Math.sqrt(s.k) * 1.4;
const names = [];                                   // district name labels, made as they are needed
const byWidth = M.P.map((p, i) => i).filter(i => M.P[i].g).sort((a, b) => M.P[b].w - M.P[a].w);   // widest districts are named first
const short = (d) => d.replace(/ (Public |Area |Community )?(School District|School Dist[.]?|Schools)$/i, "");

// ---- View ----
const MAXZ = 24, SPLIT = 3;                // deepest zoom; the zoom at which clusters split into cities
let k = 1, padL = 8, padT = 10, W = 0, H = 0, wide = true;
let z = 1, tx = 0, ty = 0;                 // zoom, and the pan offset in pixels
let ink = {};                              // colours, read from the CSS so light and dark stay in one place
const X = (p) => (padL + p.x * k) * z + tx, Y = (p) => (padT + p.y * k) * z + ty;
const shown = (m) => m.when === "always" || (m.when === "near") === (z >= SPLIT);

function layout(){
 const w = map.clientWidth; if (!w) return;
 if (w !== W) { halt(); z = 1; tx = ty = 0; }
 W = w; wide = w >= 400;
 // With room to spare, keep a left margin so practices just west of the state are labelled
 // outside it. Otherwise their labels go on the east side, over the map.
 padL = w >= 560 ? 84 : 8;
 k = (w - padL - 8) / 1000;
 H = Math.round(padT * 2 + M.h * k);
 const dpr = window.devicePixelRatio || 1;
 cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); cv.style.height = H + "px";
 svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.setAttribute("height", H);
 const css = getComputedStyle(document.documentElement);
 for (const n of ["land", "state", "edge", "s0", "s1", "s2", "s3", "s4"]) ink[n] = css.getPropertyValue("--" + n).trim();
 render();
}
// Canvas transforms for frame units, and for the tenths of a unit that district shapes use.
function frame(tenths){
 const dpr = window.devicePixelRatio || 1, s = dpr * k * z / (tenths ? 10 : 1);
 ctx.setTransform(s, 0, 0, s, dpr * (tx + padL * z), dpr * (ty + padT * z));
 return s;
}
function paint(){
 ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.clearRect(0, 0, cv.width, cv.height);
 const dpr = window.devicePixelRatio || 1;
 ctx.lineJoin = "round";
 // The state: every county outlined, then filled, which leaves only the outer edge showing.
 let s = frame(false);
 ctx.lineWidth = 3 * dpr / s; ctx.strokeStyle = ink.state; ctx.stroke(state);
 ctx.fillStyle = ink.land; ctx.fill(state);
 s = frame(true);
 fills.forEach((path, c) => { ctx.fillStyle = ink["s" + c]; ctx.fill(path, "evenodd"); });
 // Borders are exactly one device pixel wide: browsers draw that about ten times faster than
 // any other width, and the borders are most of the work in a redraw.
 ctx.lineJoin = "bevel"; ctx.lineWidth = 1 / s; ctx.strokeStyle = ink.edge; ctx.stroke(borders);
}
function render(){
 paint();
 $("over").setAttribute("transform", `translate(${tx + padL * z},${ty + padT * z}) scale(${k * z / 10})`);
 marks.forEach(m => {
  const on = shown(m);
  for (const e of [m.halo, m.ring, m.lab]) e.style.display = on ? "" : "none";
  if (!on) return;
  const s = m.s, x = X(s), y = Y(s), r = siteR(s) * (wide ? 1 : .8), textW = s.n.length * 6.8;
  for (const c of [m.halo, m.ring]) { c.setAttribute("cx", x); c.setAttribute("cy", y); c.setAttribute("r", r); }
  let east = s.x >= 500;                                  // label on the side with open space
  if (!east && x - r - 6 - textW < 2) east = true;
  if (east && x + r + 6 + textW > W - 2) east = false;
  m.lab.setAttribute("x", east ? x + r + 5 : x - r - 5);
  m.lab.setAttribute("y", y + 4);
  m.lab.setAttribute("text-anchor", east ? "start" : "end");
  // On a phone there is only room to name the larger practices until the map is zoomed in.
  if (!wide && z === 1 && s.k < 5) m.lab.style.display = "none";
  // The space this ring and its label take, so district names keep clear of it.
  m.box = [east ? x - r : x - r - 6 - textW, y - Math.max(r, 12), east ? x + r + 6 + textW : x + r, y + Math.max(r, 6)];
 });
 nameDistricts();
 map.classList.toggle("zoomed", z > 1);
 $("zin").disabled = aim() >= MAXZ; $("zout").disabled = $("zreset").disabled = aim() <= 1 && z <= 1;
 hide();
}
// Once the map is zoomed in, a district is named wherever its name fits inside it and covers
// no ring or other name, so more names appear the further in you go.
function nameDistricts(){
 let used = 0;
 if (z > 1 && !about) {                    // names wait for a zoom to settle, so they do not flicker in and out
  const taken = marks.filter(shown).map(m => m.box), dpr = window.devicePixelRatio || 1;
  const edge = (p, i) => (padL + p.b[i] * k) * z + tx, top = (p, i) => (padT + p.b[i] * k) * z + ty;
  frame(true);
  byWidth.forEach(i => {
   const p = M.P[i], text = short(p.d), half = text.length * 3.1;
   if (edge(p, 2) <= 0 || edge(p, 0) >= W || top(p, 3) <= 0 || top(p, 1) >= H) return;      // out of view
   if (half * 2 + 8 > p.w * k * z || half * 2 + 8 > W) return;
   // The name sits at the district's centre. When that is off screen, slide it to the nearest
   // spot in view, as long as that spot is still inside the district.
   const x = Math.min(W - half - 4, Math.max(half + 4, X(p))), y = Math.min(H - 8, Math.max(16, Y(p) + 4));
   if ((x !== X(p) || y !== Y(p) + 4) && !ctx.isPointInPath(shapes[i], x * dpr, (y - 4) * dpr, "evenodd")) return;
   const box = [x - half, y - 11, x + half, y + 3];
   if (taken.some(t => box[0] < t[2] && box[2] > t[0] && box[1] < t[3] && box[3] > t[1])) return;
   taken.push(box);
   const t = names[used] || (names[used] = el("text", {class: "name"}, $("names")));
   t.textContent = text; t.setAttribute("x", x); t.setAttribute("y", y); t.style.display = "";
   used++;
  });
 }
 for (let i = used; i < names.length; i++) names[i].style.display = "none";
}

// ---- Zoom and pan ----
// Keep the map inside the frame. Zoomed out past 1 (only ever briefly, see zoomAt) the map is
// smaller than the frame, so the limits swap round.
function clampPan(){
 const ex = W - W * z, ey = H - H * z;
 tx = Math.min(Math.max(0, ex), Math.max(Math.min(0, ex), tx)); ty = Math.min(Math.max(0, ey), Math.max(Math.min(0, ey), ty));
}
function clampView(){ z = Math.min(MAXZ, Math.max(1, z)); clampPan(); }
// A direct zoom, for a pinch or Ctrl + scroll: the map follows the fingers one to one. Past the
// closest or the farthest zoom it gives a little and then resists, and settle() eases it back.
let pulled = null, focal = null, wheelTimer = 0;       // pulled: the zoom the fingers have asked for, as a logarithm
function zoomAt(mx, my, factor){
 halt();
 if (pulled === null) pulled = Math.log(z);
 pulled += Math.log(factor);
 const top = Math.log(MAXZ), give = .25;
 const l = pulled > top ? top + rubber(pulled - top, give) : pulled < 0 ? -rubber(-pulled, give) : pulled;
 const z0 = z; z = Math.exp(l); focal = [mx, my];
 tx = mx - (mx - tx) * z / z0; ty = my - (my - ty) * z / z0;
 clampPan(); render();
}
function settle(){
 pulled = null;
 if (focal && (z < 1 || z > MAXZ)) zoomTo(focal[0], focal[1], z);    // zoomTo brings the target back inside the limits
}
const spot = (e) => { const box = svg.getBoundingClientRect(); return [e.clientX - box.left, e.clientY - box.top]; };

// ---- Motion ----
// A button zoom and the glide after a drag are springs rather than timed animations: they start
// from wherever the map is, keep the speed it already has, and can be caught or sent somewhere
// else at any moment. Each spring has Apple's two numbers: response, in seconds, and a damping
// ratio, where 1 settles with no bounce.
const calm = window.matchMedia("(prefers-reduced-motion: reduce)");
function spring(response, damping, rest){
 const w = 2 * Math.PI / response;
 return {x: 0, v: 0, to: 0, on: false, step(dt){
  this.v += (-w * w * (this.x - this.to) - 2 * damping * w * this.v) * dt; this.x += this.v * dt;
  if (Math.abs(this.x - this.to) < rest && Math.abs(this.v) < rest * 20) { this.x = this.to; this.v = 0; this.on = false; }
 }};
}
const sz = spring(.35, 1, .0008);                     // zoom, as its logarithm so each step feels the same size
const sx = spring(.45, 1, .2), sy = spring(.45, 1, .2);   // pan, left-right and up-down on their own
let about = null;                                     // the point the map zooms about while the zoom spring runs
let flight = false;                                   // true while flying to a district (see flyTo)
let frameId = 0, lastFrame = 0;
function halt(){ sz.on = sx.on = sy.on = false; sz.v = sx.v = sy.v = 0; about = null; flight = false; }
function run(){ if (!frameId) { lastFrame = 0; frameId = requestAnimationFrame(frameStep); } }
function frameStep(now){
 frameId = 0;
 advance(lastFrame ? Math.min(.034, (now - lastFrame) / 1000) : 1 / 60); lastFrame = now;
 if (sz.on || sx.on || sy.on) frameId = requestAnimationFrame(frameStep);
}
function advance(dt){
 const panning = sx.on || sy.on;                       // read before stepping: a spring switches itself off when it settles
 for (let n = Math.ceil(dt / .004), h = dt / n; n > 0; n--) for (const s of [sz, sx, sy]) if (s.on) s.step(h);
 if (about) {
  z = Math.exp(sz.x); tx = about.mx - about.ux * z; ty = about.my - about.uy * z;
  clampPan();
  if (!sz.on) about = null;
 } else if (flight) {
  // Flying to a district: the zoom and the point at the middle of the frame move together.
  z = Math.exp(sz.x); tx = W / 2 - sx.x * z; ty = H / 2 - sy.x * z;
  clampPan();
  if (!sz.on && !sx.on && !sy.on) flight = false;
 } else if (panning) { tx = sx.x; ty = sy.x; }
 render();
}
// Zoom to a level about a point on screen. A second press while the first is still moving
// adds to it: the spring is re-aimed from where the map is now, at the speed it has now.
function zoomTo(mx, my, target){
 target = Math.min(MAXZ, Math.max(1, target));
 pulled = null;
 if (calm.matches) return zoomAt(mx, my, target / z);
 sx.on = sy.on = false; flight = false;
 sz.x = Math.log(z); sz.to = Math.log(target); sz.on = true;
 about = {mx, my, ux: (mx - tx) / z, uy: (my - ty) / z};
 run();
}
const aim = () => sz.on ? Math.exp(sz.to) : z;        // where the zoom is heading
// Let go of a drag and the map keeps the speed of the hand, heading for where that speed would
// carry it (Apple's scroll projection), and settles there. Past an edge it eases back.
const project = (v, rate = .995) => v / 1000 * rate / (1 - rate);
function glide(vx, vy){
 flight = false;
 const lox = W - W * z, loy = H - H * z;
 sx.x = tx; sy.x = ty; sx.v = vx; sy.v = vy;
 sx.to = Math.min(0, Math.max(lox, tx + project(vx))); sy.to = Math.min(0, Math.max(loy, ty + project(vy)));
 if (calm.matches) { tx = sx.to; ty = sy.to; return render(); }
 sx.on = sy.on = true; run();
}
// Dragged past an edge, the map follows less and less instead of stopping dead.
const rubber = (over, size) => over * size * .55 / (size + .55 * over);
const band = (v, lo, size) => v > 0 ? rubber(v, size) : v < lo ? lo - rubber(lo - v, size) : v;

$("zin").addEventListener("click", () => zoomTo(W / 2, H / 2, aim() * 1.6));
$("zout").addEventListener("click", () => zoomTo(W / 2, H / 2, aim() / 1.6));
$("zreset").addEventListener("click", () => { $("pick").style.display = "none"; zoomTo(W / 2, H / 2, 1); });
// Plain scrolling stays with the page. Ctrl + scroll, or a trackpad pinch, zooms the map.
svg.addEventListener("wheel", (e) => {
 if (!e.ctrlKey && !e.metaKey) return;
 e.preventDefault();
 zoomAt(...spot(e), Math.exp(-Math.max(-50, Math.min(50, e.deltaY)) * .012));
 clearTimeout(wheelTimer); wheelTimer = setTimeout(settle, 140);     // a wheel has no "let go", so wait for it to go quiet
}, {passive: false});
svg.addEventListener("dblclick", (e) => zoomTo(...spot(e), aim() * 2));

// The mouse or one finger drags the map once it is zoomed in; two fingers pinch.
const ptrs = new Map();
let drag = null, pinch = 0, lastTap = 0, trail = [];     // trail: the last few drag positions, for the speed at release
const spread = () => { const [a, b] = [...ptrs.values()]; return {d: Math.hypot(a[0] - b[0], a[1] - b[1]), x: (a[0] + b[0]) / 2, y: (a[1] + b[1]) / 2}; };
svg.addEventListener("pointerdown", (e) => {
 halt(); pulled = null;                                // catch the map mid-flight: it stops under the finger
 ptrs.set(e.pointerId, spot(e)); trail = [];
 drag = ptrs.size === 1 ? {from: spot(e), tx, ty, moved: false} : null;
 if (ptrs.size === 2) { pinch = spread().d; hide(); }
 if (z > 1 || ptrs.size === 2) try { svg.setPointerCapture(e.pointerId); } catch (err) {}   // keep tracking outside the map
});
svg.addEventListener("pointermove", (e) => {
 if (ptrs.has(e.pointerId)) ptrs.set(e.pointerId, spot(e));
 if (ptrs.size === 2 && pinch) { const s = spread(); zoomAt(s.x, s.y, s.d / pinch); pinch = s.d; return; }
 if (drag && z > 1) {
  const [x, y] = spot(e), dx = x - drag.from[0], dy = y - drag.from[1];
  if (drag.moved || Math.hypot(dx, dy) > 4) {
   drag.moved = true; map.classList.add("dragging");
   tx = band(drag.tx + dx, W - W * z, W); ty = band(drag.ty + dy, H - H * z, H); render();
   trail.push([e.timeStamp, x, y]); while (trail.length > 2 && e.timeStamp - trail[0][0] > 100) trail.shift();
  }
  return;
 }
 if (e.pointerType === "mouse" && !ptrs.size) point(e);
});
function release(e){
 const tap = drag && !drag.moved && e.type === "pointerup", dragged = drag && drag.moved;
 ptrs.delete(e.pointerId);
 if (ptrs.size < 2 && pinch) { pinch = 0; settle(); }
 drag = null; map.classList.remove("dragging");
 if (dragged) {
  // Hand the speed of the hand to the springs, so there is no seam between dragging and gliding.
  const a = trail[0], b = trail[trail.length - 1], dt = a && b ? (b[0] - a[0]) / 1000 : 0;
  const fresh = b && e.timeStamp - b[0] < 80 && dt > 0;         // a pause before letting go means no throw
  glide(fresh ? (b[1] - a[1]) / dt : 0, fresh ? (b[2] - a[2]) / dt : 0);
 }
 if (!tap) return;
 // A second quick tap zooms in, the way a double click does with a mouse.
 if (e.pointerType !== "mouse" && Date.now() - lastTap < 320) { lastTap = 0; zoomTo(...spot(e), aim() * 2); }
 else { lastTap = Date.now(); point(e); }
}
svg.addEventListener("pointerup", release);
svg.addEventListener("pointercancel", release);
svg.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse" && !ptrs.size) hide(); });
document.addEventListener("pointerdown", (e) => { if (!map.contains(e.target)) hide(); });

// ---- Fly to a district ----
// The lookup under the map calls this when a district is picked there: the map travels to the
// district, zooms until it fills about half the frame, and keeps it outlined.
function flyTo(name){
 const p = M.P.find(d => d.d === name && d.g);
 if (!p || !W) return false;
 const bw = (p.b[2] - p.b[0]) * k, bh = (p.b[3] - p.b[1]) * k;
 const target = Math.min(MAXZ, Math.max(2, Math.min(W / bw, H / bh) * .5));
 const cx = padL + (p.b[0] + p.b[2]) / 2 * k, cy = padT + (p.b[1] + p.b[3]) / 2 * k;      // its centre, before zoom
 $("pick").setAttribute("d", p.g); $("pick").style.display = "block";
 halt(); pulled = null;
 if (calm.matches) { z = target; tx = W / 2 - cx * z; ty = H / 2 - cy * z; clampPan(); render(); return true; }
 sz.x = Math.log(z); sz.to = Math.log(target);
 sx.x = (W / 2 - tx) / z; sy.x = (H / 2 - ty) / z; sx.to = cx; sy.to = cy;
 sz.on = sx.on = sy.on = flight = true; run();
 return true;
}

// ---- Keyboard: the same moves without a pointer ----
function nudge(dx, dy){
 if (flight) sx.on = sy.on = false;                    // in flight those springs hold the frame's centre, not the pan
 sz.on = false; about = null; flight = false;
 sx.to = Math.min(0, Math.max(W - W * z, (sx.on ? sx.to : tx) + dx)); sy.to = Math.min(0, Math.max(H - H * z, (sy.on ? sy.to : ty) + dy));
 if (calm.matches) { tx = sx.to; ty = sy.to; return render(); }
 sx.x = tx; sy.x = ty; sx.on = sy.on = true; run();
}
map.addEventListener("keydown", (e) => {
 if (e.target !== map) return;                         // the zoom buttons keep their own keys
 const arrows = {ArrowLeft: [90, 0], ArrowRight: [-90, 0], ArrowUp: [0, 90], ArrowDown: [0, -90]};
 if (arrows[e.key]) { if (z > 1) { e.preventDefault(); nudge(...arrows[e.key]); } }   // not zoomed in: the arrows scroll the page as usual
 else if (e.key === "+" || e.key === "=") { e.preventDefault(); zoomTo(W / 2, H / 2, aim() * 1.6); }
 else if (e.key === "-" || e.key === "_") { e.preventDefault(); zoomTo(W / 2, H / 2, aim() / 1.6); }
 else if (e.key === "0") { e.preventDefault(); zoomTo(W / 2, H / 2, 1); }
});

// ---- Tooltip ----
// What is under the pointer: a practice ring if the pointer is on one, otherwise the district.
function under(mx, my){
 for (const {s} of marks.filter(shown)) {
  const r = siteR(s) * (wide ? 1 : .8), d = Math.hypot(X(s) - mx, Y(s) - my);
  // A ring answers along its outline; a small ring also answers inside it.
  if (d < r + 4 && (r < 9 || d > r - 5)) return {s, x: X(s), y: Y(s), r: r + 3};
 }
 const dpr = window.devicePixelRatio || 1, s = k * z;
 const ux = (mx - tx - padL * z) / s, uy = (my - ty - padT * z) / s;     // the pointer in frame units
 frame(true);
 for (let i = 0; i < M.P.length; i++) {
  const b = M.P[i].b;
  if (b && ux >= b[0] && ux <= b[2] && uy >= b[1] && uy <= b[3] && ctx.isPointInPath(shapes[i], mx * dpr, my * dpr, "evenodd")) return {p: M.P[i]};
 }
 return null;
}
function fill(b){
 tip.replaceChildren();
 const dl = document.createElement("dl");
 const row = (value, label) => dl.append(html("dt", value), html("dd", label));
 if (b.p) {
  const p = b.p;
  tip.append(html("b", p.d), html("span", p.c, "where"));
  row(p.cn + " mi", "Nearest child neurologist");
  row(p.ep + " mi", "Nearest epilepsy subspecialist");
  row(p.na + " mi", "Nearest Level 4 epilepsy center");
  if (p.ph !== "") row(p.ph + " mi", "Nearest retail pharmacy");
  row(p.ems + " min", "Ambulance, slowest 10% of calls");
  row(p.plan, "Findable seizure plan posted");
  tip.append(dl);
 } else {
  const s = b.s;
  tip.append(html("b", s.n), html("span", s.k + (s.k === 1 ? " child neurologist" : " child neurologists") + (s.m ? ": " + s.m : ""), "where"));
 }
}
let showing = null;                        // the district or practice the tooltip is about
function hide(){ tip.classList.remove("on"); $("hit").style.display = $("hitr").style.display = "none"; showing = null; }
function point(e){
 const [mx, my] = spot(e), b = under(mx, my);
 if (!b) return hide();
 if (showing !== (b.p || b.s)) {
  showing = b.p || b.s;
  fill(b);
  $("hit").style.display = b.s ? "block" : "none"; $("hitr").style.display = b.p ? "block" : "none";
  if (b.p) $("hitr").setAttribute("d", b.p.g);
  else { $("hit").setAttribute("cx", b.x); $("hit").setAttribute("cy", b.y); $("hit").setAttribute("r", b.r); }
  tip.classList.add("on");
 }
 const tw = tip.offsetWidth, th = tip.offsetHeight;
 let left = mx + 14, topPx = my + 14;
 if (left + tw > W) left = mx - 14 - tw;
 if (left < 0) left = Math.max(0, (W - tw) / 2);
 if (topPx + th > H) topPx = Math.max(0, my - 14 - th);
 tip.style.left = left + "px"; tip.style.top = topPx + "px";
 tip.style.transformOrigin = (left < mx ? "right " : "left ") + (topPx < my ? "bottom" : "top");   // grow from the pointer's side
}

// ---- Table view: every value on the map, without hovering ----
function buildTable(){
 const t = document.createElement("table");
 t.append(html("caption", `All ${M.P.length} districts, farthest from a child neurologist first. Distances in straight-line miles.`));
 const head = t.createTHead().insertRow();
 [["District"], ["County"], ["Child neurologist", 1], ["Epilepsy subspecialist", 1], ["Level 4 center", 1], ["Pharmacy", 1], ["Ambulance, slowest 10% (min)", 1], ["Seizure plan posted"]]
  .forEach(([label, num]) => { const th = html("th", label, num ? "num" : ""); th.scope = "col"; head.appendChild(th); });
 const body = t.createTBody();
 M.P.slice().sort((a, b) => b.cn - a.cn).forEach(p => {
  const tr = body.insertRow();
  [[p.d], [p.c], [p.cn, 1], [p.ep, 1], [p.na, 1], [p.ph, 1], [p.ems, 1], [p.plan]]
   .forEach(([v, num]) => tr.appendChild(html("td", v, num ? "num" : "")));
 });
 $("tablewrap").appendChild(t);
}
$("toggle").addEventListener("click", () => {
 const wrap = $("tablewrap"), open = wrap.style.display !== "block";
 if (open && !wrap.firstChild) buildTable();
 wrap.style.display = open ? "block" : "none";
 $("toggle").textContent = open ? "Hide the table" : "Show as a table";
 $("toggle").setAttribute("aria-expanded", open);
});

layout();
if ("ResizeObserver" in window) new ResizeObserver(layout).observe(map); else window.addEventListener("resize", layout);
// embed.js sets data-theme when the site switches between light and dark: repaint in the new colours.
new MutationObserver(layout).observe(document.documentElement, {attributes: true, attributeFilter: ["data-theme"]});
</script>
<script src="../js/embed.js"></script>
</body></html>"""
open(os.path.join(OUT, "care_access_map.html"), "w").write(
    CARE_MAP_HTML.replace("__MAP__", json.dumps(care_map_data(districts, providers, counties, shapes), separators=(",", ":"))))
print("wrote charts/care_access_map.html")

# lookup tool
rows = [{"d": r["district"].title(), "c": r["county"], "cn": r["nearest_child_neurology_miles"], "ep": r["nearest_epilepsy_miles"], "na": r["nearest_naec_center_miles"], "nan": r["nearest_naec_center"],
         "ph": r.get("nearest_pharmacy_miles", ""), "ems": r["ems_p90_min"], "plan": "yes" if r["classification"] == "FOUND_SEIZURE_SPECIFIC" else "no", "en": r["enrollment"]} for r in acc]
html = """<!DOCTYPE html><html lang="en" data-autoheight><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Distance to care lookup</title>
<style>:root{--fg:#232020;--bg:#fcfcfb;--card:#fff;--field:#fff;--muted:#5d5851;--line:#f0eeea;--hover:#f6e9ea;--red:#b3202c}
[data-theme=dark]{--fg:#e6e1d9;--bg:#16140f;--card:#1d1a15;--field:#1d1a15;--muted:#aaa39a;--line:#3a352e;--hover:#3a2326;--red:#ff8088}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:16px;color:var(--fg);background:var(--bg)}input{width:100%;font-size:17px;padding:10px 12px;border:2px solid #999;border-radius:8px;box-sizing:border-box;background:var(--field);color:var(--fg)}input:focus{outline:none;border-color:var(--red)}
.list{margin-top:6px;max-height:160px;overflow:auto;border:1px solid var(--line);border-radius:8px}.list:empty{display:none}.list div{padding:8px 12px;cursor:pointer}.list div:hover,.list div.active,.list div:active{background:var(--hover)}.card{margin-top:14px;padding:16px;border-left:5px solid #b3202c;background:var(--card);border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.08);animation:arrive .18s ease-out}
@keyframes arrive{from{opacity:0;transform:translateY(4px)}}@media(prefers-reduced-motion:reduce){.card{animation:none}}
.onmap{font:inherit;font-size:14px;margin-top:12px;padding:7px 12px;border:1px solid var(--line);border-radius:8px;background:transparent;color:var(--fg);cursor:pointer;transition:transform .1s ease-out}.onmap:active{transform:scale(.97)}
.row{display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-bottom:1px solid var(--line)}.row b{font-size:20px;white-space:nowrap}.far{color:var(--red)}.sub{color:var(--muted)}.note{font-size:13px;color:var(--muted);margin-top:10px}</style></head><body>
<label for="q"><strong>Type your school district</strong></label><input id="q" placeholder="e.g. Worthington, Roseau, Anoka" autocomplete="off" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="list"><div class="list" id="list" role="listbox" aria-label="Matching districts"></div><div id="out" aria-live="polite"></div>
<script>const D=__DATA__;const q=document.getElementById('q'),L=document.getElementById('list'),O=document.getElementById('out');
function show(r){const far=x=>x!==''&&parseFloat(x)>60?' class="far"':'';O.innerHTML=`<div class="card"><h3 style="margin:0 0 6px">${r.d}</h3><div class="sub">${r.c} · ${Number(r.en||0).toLocaleString()} students</div>
<div class="row"><span>Nearest child neurologist</span><b${far(r.cn)}>${r.cn} mi</b></div><div class="row"><span>Nearest epilepsy subspecialist</span><b${far(r.ep)}>${r.ep} mi</b></div><div class="row"><span>Nearest Level 4 epilepsy center</span><b${far(r.na)}>${r.na} mi</b></div>
${r.ph!==''?`<div class="row"><span>Nearest retail pharmacy</span><b${parseFloat(r.ph)>15?' class="far"':''}>${r.ph} mi</b></div>`:''}<div class="row"><span>Ambulance, slowest 10% of calls</span><b${parseFloat(r.ems)>20?' class="far"':''}>${r.ems} min</b></div><div class="row"><span>Findable seizure plan posted</span><b>${r.plan}</b></div>
<div class="note">Straight-line miles from the district office, so the drive is longer. Red means more than 60 miles to a specialist, 15 to a pharmacy, or 20 minutes for ambulances. Nearest Level 4 center: ${r.nan}. Sources: NPPES, NCES, MN OEMS, EDAN audit.</div></div>`;L.innerHTML='';
// On the Distance to Care page the map sits above this lookup: send it to the district, and offer a way up to it.
const frame=mapFrame();if(frame&&frame.contentWindow.flyTo(r.d)){const b=document.createElement('button');b.type='button';b.className='onmap';b.textContent='Show on the map';
b.onclick=()=>{frame.contentWindow.flyTo(r.d);frame.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'center'})};O.querySelector('.card').appendChild(b)}}
function mapFrame(){try{const f=parent!==window&&parent.document.querySelector('iframe[src*="care_access_map"]');return f&&f.contentWindow&&typeof f.contentWindow.flyTo==='function'?f:null}catch(e){return null}}
let M=[],ai=-1;
function pick(i){const r=M[i];if(!r)return;q.value=r.d;show(r);M=[];q.setAttribute('aria-expanded','false');q.removeAttribute('aria-activedescendant')}
q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();L.innerHTML='';ai=-1;M=v.length<2?[]:D.filter(r=>r.d.toLowerCase().includes(v)||r.c.toLowerCase().includes(v)).slice(0,12);M.forEach((r,i)=>{const e=document.createElement('div');e.textContent=r.d+' ('+r.c+')';e.id='opt-'+i;e.setAttribute('role','option');e.onclick=()=>pick(i);L.appendChild(e)});q.setAttribute('aria-expanded',M.length?'true':'false')});
// Arrow keys move through the matches, Enter picks one.
q.addEventListener('keydown',e=>{if(!M.length)return;if(e.key==='ArrowDown'){ai=Math.min(ai+1,M.length-1);e.preventDefault()}else if(e.key==='ArrowUp'){ai=Math.max(ai-1,0);e.preventDefault()}else if(e.key==='Enter'){pick(ai<0?0:ai);return}else return;[...L.children].forEach((el,i)=>{el.classList.toggle('active',i===ai);el.setAttribute('aria-selected',i===ai?'true':'false')});q.setAttribute('aria-activedescendant','opt-'+ai);L.children[ai].scrollIntoView({block:'nearest'})});</script>
<script src="../../js/embed.js"></script></body></html>""".replace("__DATA__", json.dumps(rows))
os.makedirs(os.path.join(HERE, "docs", "sims", "distance-lookup"), exist_ok=True)
open(os.path.join(HERE, "docs", "sims", "distance-lookup", "main.html"), "w").write(html); print("wrote sims/distance-lookup/main.html")

# Viewport tag and the light/dark + narrow-screen helper (docs/js/embed.js).
from postprocess_charts import finish_charts
finish_charts(OUT)
