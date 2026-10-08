#!/usr/bin/env python3
"""Build the searchable legislative district table.
Reads ../data/mn_legislative_district_profiles.csv and ../data/mn_legislative_district_schools.csv
(built by ../build_legislative_profiles.py), writes docs/legislative-districts/."""
import csv, html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUTDIR = os.path.join(HERE, "docs", "legislative-districts")

PUBLIC_PROFILE_COLS = [
    "chamber", "district", "member_2025_26", "party", "counties", "population_2020",
    "acs_under18", "acs_age_5_17", "acs_18plus",
    "est_adults_active_epilepsy", "est_adults_low", "est_adults_high",
    "est_children_under18_active_epilepsy", "est_school_age_low_1in170", "est_school_age_high_1in150",
    "est_total_active_epilepsy", "school_districts_serving", "school_districts_posting_plan",
    "school_districts_1pct_or_more", "school_districts_1pct_posting_plan",
    "pct_residents_in_district_posting_plan", "avg_miles_child_neurologist",
    "max_miles_child_neurologist", "avg_miles_epilepsy_center", "avg_miles_pharmacy", "avg_ems_p90_min",
]
PUBLIC_SCHOOL_COLS = [
    "chamber", "district", "school_district", "isd", "population_2020_in_legislative_district",
    "share_of_legislative_district_pct", "seizure_plan_classification", "plan_posted",
    "confirmation_status", "nearest_child_neurology_miles",
]

PAGE = """<!doctype html>
<html lang="en" data-autoheight><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Epilepsy by Minnesota legislative district</title>
<style>
 :root{--fg:#1a1a1a;--muted:#666;--line:#eee;--soft:#f5f5f5;--head:#fafafa;--field:#fff;--ok:#1d6b3a;--no:#8a3b12}
 [data-theme=dark]{--fg:#e6e1d9;--muted:#aaa39a;--line:#3a352e;--soft:#231f19;--head:#1d1a15;--field:#1d1a15;--ok:#6fcf97;--no:#f2a66b}
 *{box-sizing:border-box}
 body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:var(--fg)}
 .wrap{max-width:980px;margin:0 auto;padding:6px}
 .filters{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0;align-items:center}
 #q{flex:1;min-width:180px;padding:9px 12px;font-size:.95rem;border:1px solid #999;border-radius:8px;background:var(--field);color:var(--fg)}
 select{padding:8px 10px;border:1px solid #999;border-radius:8px;font-size:.88rem;background:var(--field);color:var(--fg)}
 table{border-collapse:collapse;width:100%;font-size:.86rem;margin-top:4px}
 th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--line);vertical-align:top}
 th{background:var(--head);font-size:.8rem;cursor:pointer;user-select:none}
 th:active{background:var(--soft)}                      /* a heading answers the press as it lands */
 th:focus-visible{outline:2px solid var(--muted);outline-offset:-2px}
 th[aria-sort]::after{content:" ▲";font-size:.7em;color:var(--muted)} th[aria-sort=descending]::after{content:" ▼"}
 th.r,td.r{text-align:right}
 .muted{color:var(--muted);font-size:.8rem}
 .ok{color:var(--ok);font-weight:600}.no{color:var(--no);font-weight:600}
 details{margin-top:3px} summary{cursor:pointer;color:var(--muted);font-size:.8rem}
 details ul{margin:4px 0 0 16px;padding:0;font-size:.82rem}
 @media(max-width:600px){
  thead{display:none}
  tr{display:block;padding:8px 0;border-bottom:1px solid var(--line)}
  td{display:block;border:0;padding:1px 6px;text-align:left!important}
  td:first-child{font-weight:600;font-size:.95rem}
  td:nth-child(n+2)::before{color:var(--muted)}
  td:nth-child(2)::before{content:"Member, 2025-26: "}
  td:nth-child(3)::before{content:"Residents with epilepsy (estimate): "}
  td:nth-child(4)::before{content:"Under 18 (estimate): "}
  td:nth-child(5)::before{content:"School districts posting a seizure plan: "}
  td:nth-child(6)::before{content:"Nearest child neurologist (average): "}
  td:nth-child(7)::before{content:"Ambulance, 9 in 10 calls: "}
 }
</style></head>
<body><div class="wrap">
<div class="filters">
  <input id="q" placeholder="Filter by district number, member, county or school district" aria-label="Filter districts">
  <select id="ch" aria-label="Chamber"><option value="">House and Senate</option><option>House</option><option>Senate</option></select>
</div>
<p class="muted" id="cnt"></p>
<table><thead><tr>
  <th data-k="sort">District</th><th data-k="member">Member, 2025-26</th>
  <th class="r" data-k="total">Residents with epilepsy <span style="font-weight:400">(estimate)</span></th>
  <th class="r" data-k="kids">Under 18 <span style="font-weight:400">(estimate)</span></th>
  <th data-k="pct">School districts posting a seizure plan</th>
  <th class="r" data-k="neuro">Nearest child neurologist <span style="font-weight:400">(average)</span></th>
  <th class="r" data-k="ems">Ambulance, 9 in 10 calls</th>
</tr></thead><tbody id="tb"></tbody></table>
<script>
const D=__DATA__;
let key="sort",dir=1;
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function draw(){
  const q=document.getElementById("q").value.trim().toLowerCase(),ch=document.getElementById("ch").value;
  const rows=D.filter(d=>(!ch||d.chamber===ch)&&(!q||d.hay.includes(q)))
    .sort((a,b)=>(a[key]>b[key]?1:a[key]<b[key]?-1:0)*dir);
  document.getElementById("cnt").textContent=rows.length+" of "+D.length+" districts. Select a column heading to sort.";
  document.getElementById("tb").innerHTML=rows.map(d=>`<tr>
    <td>${d.chamber} ${esc(d.district)}<div class="muted">${esc(d.counties)}</div></td>
    <td>${esc(d.member)} <span class="muted">(${d.party})</span></td>
    <td class="r">about ${d.total.toLocaleString()}</td><td class="r">about ${d.kids}</td>
    <td><b>${d.post} of ${d.n}</b> <span class="muted">covering ${Math.round(d.pct)}% of residents</span>
      <details><summary>School districts</summary><ul>${d.sd.map(s=>`<li>${esc(s[0])}, ${s[1]}%: <span class="${s[2]?"ok":"no"}">${s[2]?"plan posted":"no plan posted"}</span></li>`).join("")}</ul></details></td>
    <td class="r">${d.neuro<10?d.neuro.toFixed(1):Math.round(d.neuro)} mi</td><td class="r">${Math.round(d.ems)} min</td></tr>`).join("");
  document.querySelectorAll("th").forEach(th=>{if(th.dataset.k===key)th.setAttribute("aria-sort",dir>0?"ascending":"descending");else th.removeAttribute("aria-sort");});
}
document.getElementById("q").addEventListener("input",draw);
document.getElementById("ch").addEventListener("change",draw);
// A heading sorts by its column, by click or by Enter. The arrow on it shows which column and which way.
document.querySelectorAll("th").forEach(th=>{
  const sort=()=>{const k=th.dataset.k;dir=(k===key)?-dir:1;key=k;draw();};
  th.tabIndex=0;
  th.addEventListener("click",sort);
  th.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();sort();}});
});
draw();
</script>
<script src="../js/embed.js"></script>
</div></body></html>
"""


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    prof = list(csv.DictReader(open(os.path.join(DATA, "mn_legislative_district_profiles.csv"), encoding="utf-8")))
    sch = list(csv.DictReader(open(os.path.join(DATA, "mn_legislative_district_schools.csv"), encoding="utf-8")))
    by = {}
    for s in sch:
        by.setdefault((s["chamber"], s["district"]), []).append(s)
    data = []
    for p in prof:
        sds = [s for s in by[(p["chamber"], p["district"])] if float(s["share_of_legislative_district_pct"]) >= 1]
        counties = ", ".join(c.split(" (")[0] for c in p["counties"].split("; "))
        data.append({
            "chamber": p["chamber"], "district": p["district"],
            "sort": ("0" if p["chamber"] == "House" else "1") + p["district"],
            "member": p["member_2025_26"], "party": p["party"], "counties": counties,
            "total": int(p["est_total_rounded"]), "kids": int(p["est_children_under18_active_epilepsy"]),
            "post": int(p["school_districts_1pct_posting_plan"]), "n": int(p["school_districts_1pct_or_more"]),
            "pct": float(p["pct_residents_in_district_posting_plan"]),
            "neuro": float(p["avg_miles_child_neurologist"]), "ems": float(p["avg_ems_p90_min"]),
            "sd": [[s["school_district"], round(float(s["share_of_legislative_district_pct"])), s["plan_posted"] == "yes"] for s in sds],
            "hay": " ".join([p["chamber"], p["district"], p["district"].lstrip("0"), p["member_2025_26"], counties]
                            + [s["school_district"] for s in sds]).lower(),
        })
    page = PAGE.replace("__DATA__", json.dumps(data, separators=(",", ":")).replace("</", "<\\/"))
    open(os.path.join(OUTDIR, "district_table.html"), "w", encoding="utf-8").write(page)
    # The CSV files are shared on request and are not published with the site.
    print(f"wrote table for {len(data)} districts to {OUTDIR}")


if __name__ == "__main__":
    main()
