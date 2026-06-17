#!/usr/bin/env python3
"""Build a self-contained district lookup: search a MN district -> profile card.
Outputs textbook/docs/explore/district_lookup.html (embedded JSON + vanilla JS)."""
import csv, json, os, html

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "docs", "explore", "district_lookup.html")
CHECK_DATE = "June 2026"

def clean_isd(s):
    s = str(s).replace("ISD ", "").replace("MN-", "").strip()
    return (s[-4:].lstrip("0") or "0") if (s.startswith("0") or len(s) > 4) else (s.lstrip("0") or "0")

# roster: facts
roster = {}
for r in csv.DictReader(open(os.path.join(DATA, "mn_district_roster.csv"))):
    roster[r["isd_num"]] = r

# audit: classification (+ evidence/note from raw audit files)
ev = {}
for fn in ["audit_results_pilot.csv", "audit_results_census.csv"]:
    p = os.path.join(DATA, fn)
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            ev[clean_isd(r["isd"])] = (r.get("evidence_url", ""), r.get("note", ""))

# named contacts for priority districts (bonus)
contacts = {}
tp = os.path.join(DATA, "target_schools.csv")
if os.path.exists(tp):
    for r in csv.DictReader(open(tp)):
        contacts[str(r["ISD"]).strip()] = {"name": r.get("Best_Contact_Name", ""),
                                            "role": r.get("Contact_Role", ""),
                                            "email": r.get("Best_Contact_Email", "")}

rows = []
for r in csv.DictReader(open(os.path.join(DATA, "audit_full.csv"))):
    isd = str(r["isd"])
    ro = roster.get(isd, {})
    url, note = ev.get(isd, ("", ""))
    c = contacts.get(isd)
    rows.append({
        "isd": isd,
        "name": (r["district"] or "").title(),
        "county": (r.get("county") or "").replace(" County", ""),
        "city": (ro.get("city") or "").title(),
        "type": r.get("locale", ""),
        "enroll": ro.get("enrollment", ""),
        "phone": ro.get("phone", ""),
        "cls": r["classification"],
        "url": url if url.startswith("http") else "",
        "note": note,
        "disab": r.get("disability", ""),
        "unins": r.get("uninsured", ""),
        "contact": (f'{c["name"]} ({c["role"]})' if c and c.get("name") else ""),
        "cemail": (c["email"] if c and c.get("email", "").count("@") else ""),
    })
rows.sort(key=lambda x: x["name"])
payload = json.dumps(rows, separators=(",", ":"))

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Minnesota District Lookup</title>
<style>
 body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1a1a1a;line-height:1.55}}
 .wrap{{max-width:760px;margin:0 auto;padding:8px 4px}}
 #q{{width:100%;padding:12px 14px;font-size:1.05rem;border:1.5px solid #bbb;border-radius:10px}}
 #list{{border:1px solid #eee;border-radius:8px;margin-top:4px;max-height:240px;overflow:auto;display:none}}
 #list div{{padding:9px 12px;cursor:pointer;border-bottom:1px solid #f2f2f2;font-size:.95rem}}
 #list div:hover,#list div.active{{background:#fbeaec}}
 .muted{{color:#666;font-size:.85rem}}
 .card{{margin-top:14px;border:1px solid #e3e3e3;border-radius:12px;padding:18px;display:none}}
 .badge{{display:inline-block;padding:5px 12px;border-radius:999px;color:#fff;font-weight:600;font-size:.9rem}}
 .facts{{display:grid;grid-template-columns:1fr 1fr;gap:6px 18px;margin:14px 0;font-size:.95rem}}
 .facts b{{color:#444;font-weight:600}}
 .mean{{background:#f7f7f7;border-radius:8px;padding:10px 14px;margin:10px 0;font-size:.95rem}}
 .cta{{border-left:3px solid #b3202c;padding:8px 0 8px 14px;margin:10px 0}}
 .cta h4{{margin:0 0 4px;font-size:1rem}}
 a{{color:#b3202c}}
 .disc{{color:#777;font-size:.82rem;margin-top:14px}}
</style></head><body><div class="wrap">

<input id="q" placeholder="Type your school district or county (e.g. Worthington, St. Louis)..." autocomplete="off">
<div id="list"></div>
<p class="muted" id="hint">328 Minnesota districts. Start typing to find yours.</p>

<div class="card" id="card"></div>

<script>
const D = {payload};
const CHECK = "{CHECK_DATE}";
const LAB = {{
 FOUND_SEIZURE_SPECIFIC: ["Seizure plan posted publicly","#1a9850",
   "Good news: this district publicly posts a seizure-specific plan or page that families and staff can find."],
 FOUND_MED_POLICY_ONLY: ["Only a general medication policy found","#e08e0b",
   "This district posts a general student-medication policy, but we could not find anything that specifically mentions seizures. A seizure plan may still exist internally."],
 NOT_FOUND: ["Nothing relevant found online","#d73027",
   "We could not find a seizure plan or even a general medication policy posted online. A plan may still exist internally."],
 NOT_VERIFIABLE: ["Could not check","#888",
   "We could not access this district's policies online (site down, login required, or no policy section)."]
}};
const q=document.getElementById('q'), list=document.getElementById('list'),
      card=document.getElementById('card'), hint=document.getElementById('hint');
let matches=[], ai=-1;

function render(d){{
 const [label,color,meaning]=LAB[d.cls]||["Unknown","#888",""];
 const enroll=d.enroll&&d.enroll!=="None"?Number(d.enroll).toLocaleString()+" students":"enrollment n/a";
 let contactLine = d.cemail ? `<a href="mailto:${{d.cemail}}">${{d.contact||d.cemail}}</a>`
                   : (d.contact||"");
 card.innerHTML = `
  <span class="badge" style="background:${{color}}">${{label}}</span>
  <h2 style="margin:10px 0 2px">${{d.name}}</h2>
  <div class="muted">ISD ${{d.isd}} &middot; ${{d.city?d.city+", ":""}}${{d.county}} County &middot; ${{d.type}}</div>
  <div class="mean">${{meaning}}${{d.note?`<br><span class="muted">What we saw: ${{d.note}}</span>`:""}}</div>
  <div class="facts">
   <div><b>Enrollment:</b> ${{enroll}}</div>
   <div><b>District phone:</b> ${{d.phone||"n/a"}}</div>
   <div><b>County adult disability:</b> ${{d.disab||"n/a"}}%</div>
   <div><b>County uninsured (18-64):</b> ${{d.unins||"n/a"}}%</div>
  </div>
  ${{d.url?`<div><b>Source we checked:</b> <a href="${{d.url}}" target="_blank" rel="noopener">view district page</a></div>`:""}}
  ${{contactLine?`<div style="margin-top:6px"><b>Known health contact:</b> ${{contactLine}}</div>`:""}}
  <div class="cta"><h4>If you are a parent</h4>
   You can ask your school to set up a seizure action plan for your child, the law (Minn. Stat.
   121A.24) is on your side, whatever this status says. See the
   <a href="../chapters/06-how-to-help/index.md" target="_top">family guide and copy-paste email</a>.</div>
  <div class="cta"><h4>If you work for this district</h4>
   ${{d.cls==="FOUND_SEIZURE_SPECIFIC"
      ?"You already post a plan, thank you. A yearly review keeps it current."
      :"Closing this gap can take about 30 minutes with the free <a href='../chapters/06-how-to-help/index.md' target='_top'>drop-in packet</a> (plan template + policy language + poster)."}}</div>
  <div class="disc">Reflects what was <b>publicly findable online as of ${{CHECK}}</b>, not legal
   compliance or school safety. County health figures are community context (CDC PLACES, adults),
   not seizure rates. Wrong or out of date? Tell us via
   <a href="https://www.linkedin.com/in/krishikk/" target="_blank" rel="noopener">LinkedIn</a>.</div>`;
 card.style.display="block";
}}

function search(){{
 const s=q.value.toLowerCase().trim(); ai=-1;
 if(!s){{list.style.display="none";return;}}
 matches=D.filter(d=>(d.name+" "+d.county+" "+d.city+" "+d.isd).toLowerCase().includes(s)).slice(0,12);
 list.innerHTML=matches.map((d,i)=>`<div data-i="${{i}}">${{d.name}} <span class="muted">&middot; ${{d.county}} County</span></div>`).join("");
 list.style.display=matches.length?"block":"none";
}}
function pick(i){{ if(!matches[i])return; q.value=matches[i].name; list.style.display="none"; render(matches[i]); }}

q.addEventListener('input',search);
q.addEventListener('keydown',e=>{{
 if(list.style.display==="none")return;
 const items=[...list.children];
 if(e.key==="ArrowDown"){{ai=Math.min(ai+1,items.length-1);e.preventDefault();}}
 else if(e.key==="ArrowUp"){{ai=Math.max(ai-1,0);e.preventDefault();}}
 else if(e.key==="Enter"){{pick(ai<0?0:ai);return;}}
 else return;
 items.forEach((el,i)=>el.classList.toggle('active',i===ai));
 items[ai].scrollIntoView({{block:"nearest"}});
}});
list.addEventListener('click',e=>{{const d=e.target.closest('[data-i]');if(d)pick(+d.dataset.i);}});
</script>
</div></body></html>"""

open(OUT, "w").write(page)
print("wrote", os.path.relpath(OUT, HERE), "with", len(rows), "districts")
