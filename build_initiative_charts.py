#!/usr/bin/env python3
"""Interactive charts and lookup tools for the five initiative pages.
Reads ../data/*, writes docs/charts/*.html and docs/sims/distance-lookup/main.html."""
import csv, json, os
from collections import defaultdict
import plotly.graph_objects as go

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
fig = go.Figure(go.Bar(x=[f(r["el_share_pct"]) for r in lang][::-1], y=[r["district"].title() for r in lang][::-1], orientation="h", marker_color=RED,
    customdata=[[r["county"], r["english_learners_2021"]] for r in lang][::-1],
    hovertemplate="%{y}<br>%{x}% English learners (%{customdata[1]} students), %{customdata[0]}<br>No findable seizure plan<extra></extra>"))
fig.update_layout(title="No-plan districts with the most English learners", height=720, margin=dict(l=260, r=20, t=50, b=50))
fig.update_xaxes(title="English learners, % of enrollment (NCES 2021)", gridcolor="#eee")
save(fig, "el_noplan_districts.html")

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
fig = go.Figure()
for i, m in enumerate(mols):
    d = {int(r["year"]): f(r["prescriptions"]) for r in yr if r["molecule"] == m}
    fig.add_trace(go.Scatter(x=years, y=[d.get(y) for y in years], mode="lines+markers", name=m.replace("_", " "), visible=True if i < 6 else "legendonly",
                             hovertemplate="%{x}: %{y:,.0f} prescriptions<extra>" + m + "</extra>"))
fig.update_layout(title="Minnesota Medicaid antiseizure prescriptions by drug (click a name to show or hide)", height=520, legend=dict(orientation="v"))
fig.update_yaxes(title="Prescriptions per year", gridcolor="#eee"); fig.update_xaxes(dtick=1)
save(fig, "asm_by_molecule.html")
c25 = [(r["molecule"], f(r["total_reimbursed_usd"]) / f(r["prescriptions"]), f(r["prescriptions"])) for r in yr if r["year"] == "2025" and f(r["prescriptions"])]
c25 = sorted(c25, key=lambda x: x[1])
fig = go.Figure(go.Bar(x=[round(x[1]) for x in c25], y=[x[0].replace("_", " ") for x in c25], orientation="h", marker_color=[RED if x[1] > 500 else AMBER if x[1] > 100 else GREEN for x in c25],
    customdata=[x[2] for x in c25], hovertemplate="%{y}: $%{x:,} per prescription (%{customdata:,.0f} prescriptions in 2025)<extra></extra>"))
fig.update_xaxes(type="log", title="Average Medicaid reimbursement per prescription, 2025 (log scale)", gridcolor="#eee")
fig.update_layout(title="What a month of each seizure medicine costs", height=680, margin=dict(l=150, r=20, t=50, b=50))
save(fig, "asm_cost_per_rx.html")

# ---------- Initiative 4: interactive map + lookup ----------
acc = rd("mn_district_care_access.csv")
has_ph = "nearest_pharmacy_miles" in acc[0]
def hov(r):
    s = f"<b>{r['district'].title()}</b><br>{r['county']}<br>Nearest child neurologist: {r['nearest_child_neurology_miles']} mi<br>Nearest epilepsy specialist: {r['nearest_epilepsy_miles']} mi<br>Nearest Level 4 center: {r['nearest_naec_center_miles']} mi"
    if has_ph: s += f"<br>Nearest retail pharmacy: {r['nearest_pharmacy_miles']} mi"
    s += f"<br>Ambulance, slowest 10%: {r['ems_p90_min']} min<br>Findable seizure plan: {'yes' if r['classification']=='FOUND_SEIZURE_SPECIFIC' else 'no'}"
    return s
fig = go.Figure(go.Scattergeo(lon=[f(r["lon"]) for r in acc], lat=[f(r["lat"]) for r in acc], mode="markers",
    marker=dict(size=7, color=[f(r["nearest_child_neurology_miles"]) for r in acc], colorscale="YlOrRd", cmin=0, cmax=130, showscale=True, colorbar=dict(title="Miles to child<br>neurologist"), line=dict(width=0.3, color=INK)),
    text=[hov(r) for r in acc], hovertemplate="%{text}<extra></extra>"))
prov = [r for r in rd("mn_epilepsy_providers.csv") if r["is_child_neurology"] == "True" and r["lat"]]
fig.add_trace(go.Scattergeo(lon=[f(r["lon"]) for r in prov], lat=[f(r["lat"]) for r in prov], mode="markers", marker=dict(symbol="cross", size=7, color="#1f4e9c"), name="child neurologist", hovertemplate="Child neurologist: %{text}<extra></extra>", text=[r["city"].title() for r in prov]))
fig.update_geos(scope="usa", fitbounds="locations", showland=True, landcolor="#f7f5f2", showlakes=True, lakecolor="#dce9f5", showsubunits=True, subunitcolor="#bbb")
fig.update_layout(title="Every district's distance to pediatric epilepsy care (hover for details)", height=640, margin=dict(l=10, r=10, t=50, b=10), showlegend=False)
save(fig, "care_access_map.html")

# lookup tool
rows = [{"d": r["district"].title(), "c": r["county"], "cn": r["nearest_child_neurology_miles"], "ep": r["nearest_epilepsy_miles"], "na": r["nearest_naec_center_miles"], "nan": r["nearest_naec_center"],
         "ph": r.get("nearest_pharmacy_miles", ""), "ems": r["ems_p90_min"], "plan": "yes" if r["classification"] == "FOUND_SEIZURE_SPECIFIC" else "no", "en": r["enrollment"]} for r in acc]
html = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Distance to care lookup</title>
<style>body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;padding:16px;color:#232020;background:#fcfcfb}input{width:100%;font-size:17px;padding:10px 12px;border:2px solid #ccc;border-radius:8px;box-sizing:border-box}input:focus{outline:none;border-color:#b3202c}
.list{margin-top:6px;max-height:160px;overflow:auto;border:1px solid #eee;border-radius:8px}.list div{padding:8px 12px;cursor:pointer}.list div:hover{background:#f6e9ea}.card{margin-top:14px;padding:16px;border-left:5px solid #b3202c;background:#fff;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f0eeea}.row b{font-size:20px}.far{color:#b3202c}.note{font-size:13px;color:#5d5851;margin-top:10px}</style></head><body>
<label for="q"><strong>Type your school district</strong></label><input id="q" placeholder="e.g. Worthington, Roseau, Anoka" autocomplete="off"><div class="list" id="list"></div><div id="out"></div>
<script>const D=__DATA__;const q=document.getElementById('q'),L=document.getElementById('list'),O=document.getElementById('out');
function show(r){const far=x=>x!==''&&parseFloat(x)>60?' class="far"':'';O.innerHTML=`<div class="card"><h3 style="margin:0 0 6px">${r.d}</h3><div style="color:#5d5851">${r.c} · ${Number(r.en||0).toLocaleString()} students</div>
<div class="row"><span>Nearest child neurologist</span><b${far(r.cn)}>${r.cn} mi</b></div><div class="row"><span>Nearest epilepsy subspecialist</span><b${far(r.ep)}>${r.ep} mi</b></div><div class="row"><span>Nearest Level 4 epilepsy center</span><b${far(r.na)}>${r.na} mi</b></div>
${r.ph!==''?`<div class="row"><span>Nearest retail pharmacy</span><b${parseFloat(r.ph)>15?' class="far"':''}>${r.ph} mi</b></div>`:''}<div class="row"><span>Ambulance, slowest 10% of calls</span><b${parseFloat(r.ems)>20?' class="far"':''}>${r.ems} min</b></div><div class="row"><span>Findable seizure plan posted</span><b>${r.plan}</b></div>
<div class="note">Straight-line miles from the district office; rural drive time is about a third longer. Red means more than 60 miles to a specialist, 15 to a pharmacy, or 20 minutes for ambulances. Nearest Level 4 center: ${r.nan}. Sources: NPPES, NCES, MN OEMS, EDAN audit.</div></div>`;L.innerHTML='';}
q.addEventListener('input',()=>{const v=q.value.trim().toLowerCase();L.innerHTML='';if(v.length<2)return;D.filter(r=>r.d.toLowerCase().includes(v)||r.c.toLowerCase().includes(v)).slice(0,12).forEach(r=>{const e=document.createElement('div');e.textContent=r.d+' ('+r.c+')';e.onclick=()=>{q.value=r.d;show(r)};L.appendChild(e)})});</script></body></html>""".replace("__DATA__", json.dumps(rows))
os.makedirs(os.path.join(HERE, "docs", "sims", "distance-lookup"), exist_ok=True)
open(os.path.join(HERE, "docs", "sims", "distance-lookup", "main.html"), "w").write(html); print("wrote sims/distance-lookup/main.html")
