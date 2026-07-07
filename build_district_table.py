#!/usr/bin/env python3
"""Build a searchable three-layer district table for the Find Your District page.
Outputs textbook/docs/find-your-district/district_table.html"""
import csv, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT  = os.path.join(HERE, "docs", "find-your-district", "district_table.html")
CHECK_DATE = "June 2026"

PLAN_LABEL = {
    "FOUND_SEIZURE_SPECIFIC": ("Plan posted",          "#1a9850", "yes"),
    "FOUND_MED_POLICY_ONLY":  ("Medication policy only","#e08e0b", "med"),
    "NOT_FOUND":              ("Nothing found online", "#d73027", "no"),
    "NOT_VERIFIABLE":         ("Could not check",      "#999999", "unk"),
}
NURSE_LABEL = {
    "ZERO_SUPPORT_STAFF":  ("Likely no nurse",  "#b71c1c"),
    "HIGH_RISK_SMALL":     ("Likely no nurse",  "#e65100"),
    "ELEVATED_RISK_MID":   ("Possibly no nurse","#f57f17"),
    "LOW_RISK_LARGE":      ("Likely yes",       "#2e7d32"),
}

def ems_label(val):
    try:
        m = float(val)
        if m >= 15: return (f"{m:.0f} min avg", "#b71c1c")
        if m >= 12: return (f"{m:.0f} min avg", "#e65100")
        if m >= 10: return (f"{m:.0f} min avg", "#f57f17")
        return (f"{m:.0f} min avg", "#2e7d32")
    except: return ("n/a", "#999")

ev = {}
for fn in ["audit_results_pilot.csv", "audit_results_census.csv"]:
    p = os.path.join(DATA, fn)
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            isd = str(r["isd"]).replace("ISD ","").replace("MN-","").strip().lstrip("0") or "0"
            ev[isd] = r.get("evidence_url", "")

composite = {}
cp = os.path.join(DATA, "mn_district_risk_composite.csv")
if os.path.exists(cp):
    for r in csv.DictReader(open(cp)):
        composite[str(r["isd"])] = r

rows = sorted(csv.DictReader(open(os.path.join(DATA, "audit_full.csv"))),
              key=lambda r: r["district"].title())
trs = []
for r in rows:
    isd = str(r["isd"])
    c   = composite.get(isd, {})
    pl, pc, ptag = PLAN_LABEL.get(r["classification"], ("Unknown","#999","unk"))
    nl, nc = NURSE_LABEL.get(c.get("nurse_risk_tier",""), ("Unknown","#999"))
    el, ec = ems_label(c.get("ems_avg_min",""))
    url  = ev.get(isd, "")
    link = f'<a href="{html.escape(url)}" target="_blank" rel="noopener">source</a>' if url.startswith("http") else "&ndash;"
    name   = html.escape(r["district"].title())
    county = html.escape((r.get("county") or "").replace(" County",""))
    dual   = str(c.get("dual_risk","")).lower() == "true"
    dual_tag = ' <span style="background:#fce4ec;color:#880e4f;font-size:.72rem;padding:1px 6px;border-radius:10px;font-weight:600">DUAL RISK</span>' if dual else ""
    trs.append(
        f'<tr data-s="{html.escape((name+" "+county+" "+isd).lower())}" data-plan="{ptag}">'
        f'<td>{name}{dual_tag}</td>'
        f'<td>{county}</td>'
        f'<td>{html.escape(r.get("locale",""))}</td>'
        f'<td><span class="dot" style="background:{pc}"></span>{pl}</td>'
        f'<td><span class="dot" style="background:{nc}"></span>{nl}</td>'
        f'<td><span class="dot" style="background:{ec}"></span>{el}</td>'
        f'<td>{link}</td></tr>')

n = len(rows)
n_plan = sum(1 for r in rows if r["classification"] == "FOUND_SEIZURE_SPECIFIC")

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>All Minnesota districts: seizure readiness</title>
<style>
 body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1a1a1a}}
 .wrap{{max-width:980px;margin:0 auto;padding:6px}}
 .filters{{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0;align-items:center}}
 #q{{flex:1;min-width:180px;padding:9px 12px;font-size:.95rem;border:1px solid #bbb;border-radius:8px}}
 select{{padding:8px 10px;border:1px solid #bbb;border-radius:8px;font-size:.88rem}}
 .freshness{{font-size:.78rem;color:#666;margin:4px 0 8px;display:flex;gap:12px;flex-wrap:wrap}}
 .freshness span{{background:#f5f5f5;border-radius:20px;padding:2px 9px}}
 table{{border-collapse:collapse;width:100%;font-size:.86rem;margin-top:4px}}
 th,td{{text-align:left;padding:6px 8px;border-bottom:1px solid #eee}}
 th{{position:sticky;top:0;background:#fafafa;font-size:.8rem;white-space:nowrap}}
 .dot{{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:middle}}
 .muted{{color:#666;font-size:.8rem}} a{{color:#b3202c}}
 @media(max-width:600px){{td:nth-child(6),th:nth-child(6){{display:none}}}}
</style></head><body><div class="wrap">
<div class="freshness">
  <span>Seizure plan audit: <b>June 2026</b></span>
  <span>Nurse coverage: <b>NCES 2023-24 est.</b></span>
  <span>EMS times: <b>2023 county data</b></span>
</div>
<p class="muted">{n} Minnesota districts. {n_plan} post a seizure-specific plan publicly online.
"Not found" does not mean no plan; always contact your school directly.</p>
<div class="filters">
  <input id="q" placeholder="Filter by district or county…">
  <select id="f-plan" onchange="filt()">
    <option value="">All seizure plans</option>
    <option value="yes">Plan posted</option>
    <option value="med">Medication policy only</option>
    <option value="no">Nothing found</option>
  </select>
  <select id="f-dual" onchange="filt()">
    <option value="">All districts</option>
    <option value="dual">Dual risk only</option>
  </select>
</div>
<p class="muted" id="cnt"></p>
<table><thead><tr>
  <th>District</th><th>County</th><th>Type</th>
  <th>Seizure plan <span style="font-weight:400">(June 2026)</span></th>
  <th>School nurse <span style="font-weight:400">(est. 2023-24)</span></th>
  <th>EMS response <span style="font-weight:400">(2023 county avg)</span></th>
  <th>Source</th>
</tr></thead>
<tbody id="tb">
{chr(10).join(trs)}
</tbody></table>
<script>
function filt(){{
 var q=document.getElementById('q').value.toLowerCase().trim();
 var fp=document.getElementById('f-plan').value;
 var fd=document.getElementById('f-dual').value;
 var rows=document.querySelectorAll('#tb tr'), n=0;
 rows.forEach(function(r){{
   var ms=r.getAttribute('data-s').indexOf(q)>-1;
   var mp=!fp||r.getAttribute('data-plan')===fp;
   var md=!fd||(fd==='dual'&&r.innerHTML.indexOf('DUAL RISK')>-1);
   var show=ms&&mp&&md; r.style.display=show?'':'none'; if(show)n++;
 }});
 document.getElementById('cnt').textContent=n+' districts shown';
}}
document.getElementById('q').addEventListener('input',filt);
filt();
</script>
</div></body></html>"""
open(OUT, "w").write(page)
print("wrote", os.path.relpath(OUT, HERE), "with", n, "districts")
