#!/usr/bin/env python3
"""Build the searchable county table.
Reads ../data/mn_county_epilepsy_profiles.csv (built by ../build_county_profiles.py),
writes docs/counties/."""
import csv, json, os
from build_legislative_table import PAGE as LEG_PAGE

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUTDIR = os.path.join(HERE, "docs", "counties")

STYLE = LEG_PAGE[LEG_PAGE.index("<style>"):LEG_PAGE.index("@media(max-width:600px){")]
PAGE = """<!doctype html>
<html lang="en" data-autoheight><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Epilepsy by Minnesota county</title>
""" + STYLE + """ @media(max-width:600px){
  thead{display:none}
  tr{display:block;padding:8px 0;border-bottom:1px solid var(--line)}
  td{display:block;border:0;padding:1px 6px;text-align:left!important}
  td:first-child{font-weight:600;font-size:.95rem}
  td:nth-child(n+2)::before{color:var(--muted)}
  td:nth-child(2)::before{content:"Residents with epilepsy (estimate): "}
  td:nth-child(3)::before{content:"Under 18 (estimate): "}
  td:nth-child(4)::before{content:"School districts posting a seizure plan: "}
  td:nth-child(5)::before{content:"Child neurologists in the county: "}
  td:nth-child(6)::before{content:"Nearest child neurologist (typical district): "}
  td:nth-child(7)::before{content:"Ambulance, 9 in 10 calls: "}
  td:nth-child(8)::before{content:"Deaths with epilepsy or seizures, 2018 to 2024: "}
 }
 .scroll{overflow-x:auto} th{white-space:normal} th,td{padding:6px 6px}
 td .muted{font-size:.74rem}
</style></head>
<body><div class="wrap">
<div class="filters">
  <input id="q" placeholder="Filter by county" aria-label="Filter counties">
  <select id="ru" aria-label="Type of county"><option value="">All counties</option><option>Metropolitan</option><option>Nonmetro-Urban</option><option>Nonmetro-Large Town</option><option>Rural</option></select>
</div>
<p class="muted" id="cnt"></p>
<p class="muted">With epilepsy and under 18 are estimates. Child neurologists are those practicing in the county; miles are to the nearest one from a typical school district. Ambulance is minutes to reach 9 in 10 emergency calls. Deaths are death certificates that mention epilepsy or seizures.</p>
<div class="scroll"><table><thead><tr>
  <th data-k="county">County</th>
  <th class="r" data-k="total">With epilepsy <span style="font-weight:400">(est.)</span></th>
  <th class="r" data-k="kids">Under 18 <span style="font-weight:400">(est.)</span></th>
  <th data-k="pct">Districts posting a seizure plan</th>
  <th class="r" data-k="child">Child neuro-logists</th>
  <th class="r" data-k="neuro">Miles to nearest</th>
  <th class="r" data-k="ems">Ambu-lance</th>
  <th class="r" data-k="deaths">Deaths, 2018 to 2024</th>
</tr></thead><tbody id="tb"></tbody></table></div>
<script>
const D=__DATA__;
let key="county",dir=1;
function draw(){
  const q=document.getElementById("q").value.trim().toLowerCase(),ru=document.getElementById("ru").value;
  const rows=D.filter(d=>(!ru||d.ru===ru)&&(!q||d.county.toLowerCase().includes(q)))
    .sort((a,b)=>(a[key]>b[key]?1:a[key]<b[key]?-1:0)*dir);
  document.getElementById("cnt").textContent=rows.length+" of "+D.length+" counties. Select a column heading to sort.";
  document.getElementById("tb").innerHTML=rows.map(d=>`<tr>
    <td>${d.county}<div class="muted">${d.pop.toLocaleString()}, ${d.ru}</div></td>
    <td class="r">about ${d.total.toLocaleString()}</td><td class="r">about ${d.kids.toLocaleString()}</td>
    <td><b>${d.post} of ${d.n}</b> <span class="muted">(${Math.round(d.pct)}% of students)</span></td>
    <td class="r">${d.child}</td>
    <td class="r">${d.neuro<10?d.neuro.toFixed(1):Math.round(d.neuro)} mi</td><td class="r">${Math.round(d.ems)} min</td>
    <td class="r">${d.deaths<0?"under 10":d.deaths.toLocaleString()}</td></tr>`).join("");
  document.querySelectorAll("th").forEach(th=>{if(th.dataset.k===key)th.setAttribute("aria-sort",dir>0?"ascending":"descending");else th.removeAttribute("aria-sort");});
}
document.getElementById("q").addEventListener("input",draw);
document.getElementById("ru").addEventListener("change",draw);
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
    prof = list(csv.DictReader(open(os.path.join(DATA, "mn_county_epilepsy_profiles.csv"), encoding="utf-8")))
    data = []
    for p in prof:
        d = p["deaths_any_seizure_mention_2018_2024"]
        data.append({
            "county": p["county"].replace(" County", ""), "ru": p["rural_urban_category"], "pop": int(p["population_2025"]),
            "total": int(p["est_total_rounded"]), "kids": int(p["est_children_under18_active_epilepsy"]),
            "post": int(p["school_districts_posting_plan"]), "n": int(p["school_districts"]),
            "pct": float(p["pct_students_in_district_posting_plan"] or 0),
            "child": int(p["child_neurologists_in_county"]), "neuro": float(p["median_miles_child_neurologist"]),
            "ems": float(p["ems_p90_min_2023"]),
            "deaths": -1 if d == "Suppressed" else int(d.replace(",", "")),
        })
    open(os.path.join(OUTDIR, "county_table.html"), "w", encoding="utf-8").write(
        PAGE.replace("__DATA__", json.dumps(data, separators=(",", ":"))))
    # The CSV file is shared on request and is not published with the site.
    print(f"wrote county table for {len(data)} counties to {OUTDIR}")


if __name__ == "__main__":
    main()
