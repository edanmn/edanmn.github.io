#!/usr/bin/env python3
"""Build a self-contained district lookup: search a MN district -> profile card.
Reads ../data/*. Writes docs/find-your-district/district_lookup.html (embedded JSON + vanilla
JS) and the public data file docs/data/mn_seizure_plan_audit.csv, and keeps the reply counts
on the report page in step with the data."""
import csv, json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
OUT = os.path.join(HERE, "docs", "find-your-district", "district_lookup.html")
CHECK_DATE = "June 2026"

def clean_isd(s):
    s = str(s).replace("ISD ", "").replace("MN-", "").strip()
    return (s[-4:].lstrip("0") or "0") if s.startswith("0") else (s.lstrip("0") or "0")

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

# composite risk data (nurse + EMS layers)
composite = {}
cp = os.path.join(DATA, "mn_district_risk_composite.csv")
if os.path.exists(cp):
    for r in csv.DictReader(open(cp)):
        composite[str(r["isd"])] = r

# Licensed school nurse (LSN) estimate from district size (MDH 2022 statewide rates).
# It is an estimate, not a count for the district.
NURSE_LABEL = {
    "ZERO_SUPPORT_STAFF": ("Likely none",   "#b71c1c"),
    "HIGH_RISK_SMALL":    ("Likely none",   "#e65100"),
    "ELEVATED_RISK_MID":  ("Possibly none", "#f57f17"),
    "LOW_RISK_LARGE":     ("Likely yes",    "#2e7d32"),
}

def short_month(m):
    return m.replace("September", "Sept")

# Districts whose September 2026 re-check found a seizure plan form or handbook section posted
# after the June audit. Their June classification stays, but they are not shown as dual risk.
RECHECK_FOUND = {"345", "2898"}

def nurse_reply(rec):
    """If the district's email reply came from a nurse, say so instead of the size estimate."""
    if not rec: return None
    role = rec.get("respondent_role", "").lower()
    when = short_month(rec.get("confirmed_month", ""))
    if "licensed school nurse" in role: return (f"Licensed school nurse replied ({when})", "#2e7d32")
    if "nurs" in role: return (f"School nurse replied ({when}); license not stated", "#1a73e8")
    return None

def ems_text(val):
    try:
        m = float(val)
        if m >= 15: return (f"{m:.0f} min county avg (critical)", "#b71c1c")
        if m >= 12: return (f"{m:.0f} min county avg (high)", "#e65100")
        if m >= 10: return (f"{m:.0f} min county avg (elevated)", "#f57f17")
        return (f"{m:.0f} min county avg", "#2e7d32")
    except: return ("n/a", "#999")

# named contacts for priority districts (bonus)
contacts = {}
tp = os.path.join(DATA, "target_schools.csv")
if os.path.exists(tp):
    for r in csv.DictReader(open(tp)):
        contacts[str(r["ISD"]).strip()] = {"name": r.get("Best_Contact_Name", ""),
                                            "role": r.get("Contact_Role", ""),
                                            "email": r.get("Best_Contact_Email", "")}

# districts that confirmed by email that they have plans on file and trained staff
confirmed = {}
responded = {}   # replied, but no confirmed plan yet (in progress or pending)
cfp = os.path.join(DATA, "district_confirmations.csv")
if os.path.exists(cfp):
    for r in csv.DictReader(open(cfp)):
        if r.get("status", "confirmed") == "confirmed":
            confirmed[str(r["isd"])] = r
        else:
            responded[str(r["isd"])] = r

rows = []
for r in csv.DictReader(open(os.path.join(DATA, "audit_full.csv"))):
    isd = str(r["isd"])
    ro  = roster.get(isd, {})
    c   = contacts.get(isd)
    url, note = ev.get(isd, ("", ""))
    comp = composite.get(isd, {})
    nl, nc = NURSE_LABEL.get(comp.get("nurse_risk_tier",""), ("Unknown","#999"))
    rec = confirmed.get(isd) or responded.get(isd)
    nurse_rep = nurse_reply(rec)
    if nurse_rep: nl, nc = nurse_rep
    et, ec = ems_text(comp.get("ems_avg_min",""))
    # Dual risk: no plan posted AND a small district likely without an LSN. Only for districts we
    # could check, and dropped once a district confirms plans or a nurse has replied.
    dual = (str(comp.get("dual_risk","")).lower() == "true"
            and r["classification"] in ("FOUND_MED_POLICY_ONLY", "NOT_FOUND")
            and isd not in confirmed and not nurse_rep and isd not in RECHECK_FOUND)
    rows.append({
        "isd":   isd,
        "name":  (r["district"] or "").title(),
        "county":(r.get("county") or "").replace(" County", ""),
        "city":  (ro.get("city") or "").title(),
        "type":  r.get("locale", ""),
        "enroll":ro.get("enrollment", ""),
        "phone": ro.get("phone", ""),
        "cls":   r["classification"],
        "url":   url if url.startswith("http") else "",
        "note":  note,
        "disab": r.get("disability", ""),
        "unins": r.get("uninsured", ""),
        "contact":(f'{c["name"]} ({c["role"]})' if c and c.get("name") else ""),
        "cemail":(c["email"] if c and c.get("email", "").count("@") else ""),
        "nl": nl, "nc": nc,
        "et": et, "ec": ec,
        "dual": dual,
        "recheck": isd in RECHECK_FOUND,
        "cmonth": short_month(confirmed[isd]["confirmed_month"]) if isd in confirmed else "",
        "conf": (f'{confirmed[isd]["respondent_role"]} confirmed by email in {confirmed[isd]["confirmed_month"]}: '
                 f'{confirmed[isd]["what_confirmed"]}') if isd in confirmed else "",
        "resp": (f'{responded[isd]["respondent_role"]} told us by email in {responded[isd]["confirmed_month"]} that '
                 f'{responded[isd]["what_confirmed"]}.') if isd in responded else "",
        "rstat": responded[isd]["status"] if isd in responded else "",
    })
rows.sort(key=lambda x: x["name"])
payload = json.dumps(rows, separators=(",", ":"))

# ---- Public data file, linked from the Data and methods page ----
# One row per district with the audit result. Phone numbers and named contacts stay out of it.
CSV_OUT = os.path.join(HERE, "docs", "data", "mn_seizure_plan_audit.csv")
CLS_LABEL = {
    "FOUND_SEIZURE_SPECIFIC": "Seizure plan posted",
    "FOUND_MED_POLICY_ONLY":  "Medication policy only",
    "NOT_FOUND":              "Nothing found",
    "NOT_VERIFIABLE":         "Could not check",
}

def write_public_csv(rows, path=CSV_OUT, check_date=CHECK_DATE):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["isd", "district", "county", "city", "locale", "enrollment", "classification",
                    "classification_label", "what_we_saw", "source_url", "checked",
                    "posted_since_check", "district_reply", "district_reply_summary"])
        for r in rows:
            w.writerow([r["isd"], r["name"], r["county"], r["city"], r["type"],
                        "" if r["enroll"] in ("", "None") else r["enroll"], r["cls"],
                        CLS_LABEL.get(r["cls"], ""), r["note"], r["url"], check_date,
                        "yes" if r["recheck"] else "",
                        "confirmed" if r["conf"] else r["rstat"], r["conf"] or r["resp"]])
    print("wrote", os.path.relpath(path, HERE), "with", len(rows), "districts")

# ---- Reply counts on the report page ----
# The sentence is typed into the page, so its two numbers are rewritten whenever the data changes.
REPORT_MD = os.path.join(HERE, "docs", "programs", "report-your-district", "index.md")

def update_reply_counts(rows, path=REPORT_MD):
    replied = sum(1 for r in rows if r["conf"] or r["resp"])
    confirmed = sum(1 for r in rows if r["conf"])
    text = open(path, encoding="utf-8").read()
    new, n = re.subn(r"So far \d+ districts have replied and \d+ are confirmed\.",
                     f"So far {replied} districts have replied and {confirmed} are confirmed.", text)
    if n != 1:
        print("WARNING: reply-count sentence not found in", os.path.relpath(path, HERE))
    elif new != text:
        open(path, "w", encoding="utf-8").write(new)
        print("updated reply counts:", replied, "replied,", confirmed, "confirmed")

page = f"""<!doctype html>
<html lang="en" data-autoheight><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Minnesota District Lookup</title>
<style>
 :root{{--fg:#1a1a1a;--muted:#666;--line:#e3e3e3;--soft:#f7f7f7;--field:#fff;--link:#b3202c;--hover:#fbeaec;--ok:#e6f4ea;--info:#e8f0fe}}
 [data-theme=dark]{{--fg:#e6e1d9;--muted:#aaa39a;--line:#3a352e;--soft:#231f19;--field:#1d1a15;--link:#ff8088;--hover:#3a2326;--ok:#16301f;--info:#17263f}}
 *{{box-sizing:border-box}}
 body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:var(--fg);line-height:1.55}}
 .wrap{{max-width:760px;margin:0 auto;padding:8px 4px}}
 label{{display:block;font-weight:600;font-size:.95rem;margin:0 0 6px}}
 #q{{width:100%;padding:12px 14px;font-size:1.05rem;border:1.5px solid #999;border-radius:10px;background:var(--field);color:var(--fg)}}
 #q:focus-visible{{outline:3px solid var(--link);outline-offset:1px}}
 #list{{border:1px solid var(--line);border-radius:8px;margin-top:4px;max-height:240px;overflow:auto;display:none}}
 #list div{{padding:9px 12px;cursor:pointer;border-bottom:1px solid var(--line);font-size:.95rem}}
 #list div:hover,#list div.active{{background:var(--hover)}}
 .muted{{color:var(--muted);font-size:.85rem}}
 .card{{margin-top:14px;border:1px solid var(--line);border-radius:12px;padding:18px;display:none}}
 .badge{{display:inline-block;padding:5px 12px;border-radius:999px;font-weight:600;font-size:.9rem}}
 .pill{{display:inline-block;padding:3px 10px;border-radius:12px;font-size:.8rem;font-weight:600}}
 .dual{{display:inline-block;margin-left:8px;background:#fce4ec;color:#880e4f;font-size:.78rem;padding:2px 9px;border-radius:12px;font-weight:600}}
 .layers{{width:100%;font-size:.88rem;border-collapse:collapse;margin:12px 0}}
 .layers tr+tr{{border-top:1px solid var(--line)}}
 .layers td{{padding:6px 4px}}
 .layers .k{{color:var(--muted);font-size:.76rem}}
 .layers .k span{{font-size:.7rem}}
 .facts{{display:grid;grid-template-columns:1fr 1fr;gap:6px 18px;margin:14px 0;font-size:.95rem}}
 .facts b{{font-weight:600}}
 .mean{{background:var(--soft);border-radius:8px;padding:10px 14px;margin:10px 0;font-size:.95rem}}
 .mean.ok{{background:var(--ok);border-left:3px solid #1a9850}}
 .mean.info{{background:var(--info);border-left:3px solid #1a73e8}}
 .cta{{border-left:3px solid #b3202c;padding:8px 0 8px 14px;margin:10px 0}}
 .cta h4{{margin:0 0 4px;font-size:1rem}}
 a{{color:var(--link)}}
 .share{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:14px 0 0}}
 .share button{{font:inherit;font-size:.88rem;padding:7px 12px;border:1px solid var(--line);border-radius:8px;background:var(--soft);color:var(--fg);cursor:pointer}}
 .share button:hover{{border-color:var(--link)}}
 .share span{{word-break:break-all}}
 .disc{{color:var(--muted);font-size:.82rem;margin-top:14px}}
 @media(max-width:480px){{.card{{padding:14px}}.facts{{grid-template-columns:1fr}}}}
</style></head><body><div class="wrap">

<label for="q">Search by district or county</label>
<input id="q" placeholder="e.g. Worthington, St. Louis" autocomplete="off"
       role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="list">
<div id="list" role="listbox" aria-label="Matching districts"></div>
<p class="muted" id="hint" aria-live="polite">{len(rows)} Minnesota districts. Start typing to find yours.</p>

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
const HINT = "{len(rows)} Minnesota districts. Start typing to find yours.";
const q=document.getElementById('q'), list=document.getElementById('list'),
      card=document.getElementById('card'), hint=document.getElementById('hint');
let matches=[], ai=-1;

// Readable text on any badge colour: white where it has the contrast, dark ink where it does not.
function lum(h){{
 h=h.replace("#",""); if(h.length===3)h=h.replace(/./g,"$&$&");
 const c=[0,2,4].map(i=>parseInt(h.substr(i,2),16)/255).map(v=>v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4));
 return .2126*c[0]+.7152*c[1]+.0722*c[2];
}}
function ink(bg){{const L=lum(bg)+.05; return 1.05/L>=L/.0603?"#fff":"#1a1a1a";}}
const paint=(bg)=>`background:${{bg}};color:${{ink(bg)}}`;

// Shareable links. Inside the Find Your District page the address bar belongs to the parent
// page, so it is read and written there: ?district=<ISD number> opens that district and
// ?find=<text> pre-fills the search (the home page search box sends this).
const page=(()=>{{try{{return parent.location.href?parent:window;}}catch(e){{return window;}}}})();
function linkFor(isd){{
 const u=new URL(page.location.href); u.hash=""; u.search=""; u.searchParams.set("district",isd); return u.href;
}}
function remember(isd){{
 try{{
  const u=new URL(page.location.href); u.searchParams.delete("find"); u.searchParams.set("district",isd);
  page.history.replaceState(page.history.state,"",u.href);
 }}catch(e){{}}
}}

function render(d){{
 const [label0,color0,meaning]=LAB[d.cls]||["Unknown","#888",""];
 // A district that confirmed by email gets a badge that says so, unless it also posts a plan.
 const confBadge = d.conf && d.cls!=="FOUND_SEIZURE_SPECIFIC";
 const label = !confBadge ? label0
   : d.cls==="NOT_VERIFIABLE" ? `Confirmed by district email, ${{d.cmonth}}`
   : `Not posted online; confirmed by district email, ${{d.cmonth}}`;
 const color = confBadge ? "#1a9850" : color0;
 const enroll=d.enroll&&d.enroll!=="None"?Number(d.enroll).toLocaleString()+" students":"enrollment n/a";
 let contactLine = d.cemail ? `<a href="mailto:${{d.cemail}}">${{d.contact||d.cemail}}</a>`
                   : (d.contact||"");
 const dualBadge = d.dual ? `<span class="dual">DUAL RISK</span>` : "";
 const efmn = `For help with a child's plan, contact the <a href="https://www.epilepsyfoundationmn.org/" target="_blank" rel="noopener">Epilepsy Foundation of Minnesota</a>.`;
 const ctaText = (d.conf
   ? `This district replied to us by email about its seizure plans; its reply is summarized above.`
   : d.rstat==="in_progress"
     ? `This district told us it is working on its seizure plans.`
   : d.rstat==="pending"
     ? `This district told us a plan was on file last school year and has not yet confirmed this year.`
   : d.recheck
     ? `Since our June check, this district has posted a seizure action plan form or handbook section.`
   : d.cls==="NOT_VERIFIABLE"
     ? `We could not check this district's site.`
   : d.dual
     ? `This district posts no seizure plan online, and districts its size often have no licensed school nurse.`
   : d.cls!=="FOUND_SEIZURE_SPECIFIC"
     ? `We found no public seizure plan. A district may still have one on file.`
     : `A seizure plan is posted.`) + " " + efmn;
 card.innerHTML = `
  <span class="badge" style="${{paint(color)}}">${{label}}</span>${{dualBadge}}
  <h2 style="margin:10px 0 2px">${{d.name}}</h2>
  <div class="muted">${{d.isd==="30001"?"SSD 1":"ISD "+d.isd}} &middot; ${{d.city?d.city+", ":""}}${{d.county}} County &middot; ${{d.type}}</div>
  ${{d.conf?`<div class="mean ok"><b>&#10003; Confirmed by the district.</b> ${{d.conf}}. Our website check found: ${{label0.toLowerCase()}}.</div>`:""}}
  ${{d.resp?`<div class="mean info"><b>${{d.rstat==="in_progress"?"District update: working on a plan.":"District update: awaiting confirmation."}}</b> ${{d.resp}} We will update this entry when the district confirms a plan is in place.</div>`:""}}
  <div class="mean">${{meaning}}${{d.note?`<br><span class="muted">What we saw: ${{d.note}}</span>`:""}}</div>
  <table class="layers">
   <tr>
    <td class="k">SEIZURE PLAN POSTED<br><span>Checked ${{CHECK}}</span></td>
    <td><span class="badge" style="${{paint(color0)}};font-size:.8rem">${{label0}}</span></td>
   </tr>
   <tr>
    <td class="k">LICENSED SCHOOL NURSE<br><span>Estimate from district size (MDH 2022)</span></td>
    <td><span class="pill" style="${{paint(d.nc)}}">${{d.nl}}</span></td>
   </tr>
   <tr>
    <td class="k">EMS RESPONSE TIME<br><span>2023 county average</span></td>
    <td><span class="pill" style="${{paint(d.ec)}}">${{d.et}}</span></td>
   </tr>
  </table>
  <div class="facts">
   <div><b>Enrollment:</b> ${{enroll}}</div>
   <div><b>District phone:</b> ${{d.phone||"n/a"}}</div>
   <div><b>County adult disability:</b> ${{d.disab||"n/a"}}%</div>
   <div><b>County uninsured (18-64):</b> ${{d.unins||"n/a"}}%</div>
  </div>
  ${{d.url?`<div style="margin:6px 0"><b>Source we checked:</b> <a href="${{d.url}}" target="_blank" rel="noopener">view district page</a></div>`:""}}
  ${{contactLine?`<div style="margin:6px 0"><b>Known health contact:</b> ${{contactLine}}</div>`:""}}
  <div class="cta"><h4>For parents</h4>${{ctaText}}</div>
  <div class="cta"><h4>If you work for this district</h4>
   ${{d.cls==="FOUND_SEIZURE_SPECIFIC"
      ?"You already post a plan, thank you. A yearly review keeps it current."
      :d.conf
      ?"Thank you for confirming. Posting a blank plan template or a short seizure page online helps families and substitute staff find it; the free <a href='../packet/EDAN-Seizure-Safe-Schools-Packet.pdf' target='_top'>packet</a> has one ready."
      :"Use the free <a href='../packet/EDAN-Seizure-Safe-Schools-Packet.pdf' target='_top'>drop-in packet</a> (plan template + Policy 516 language + poster). Note: the current MSBA Model Policy 516 does not reference Minn. Stat. 121A.24, and the drop-in language fixes this."}}</div>
  <div class="share"><button type="button" id="copy">Copy link to this result</button><span class="muted" id="copied" aria-live="polite"></span></div>
  <div class="disc">Seizure plan reflects what was <b>publicly findable as of ${{CHECK}}</b>. Licensed school nurse status is an estimate from district size, based on MDH 2022 statewide rates and NCES 2023-24 staffing data, not a count for this district, unless a district nurse has replied to us. EMS times are 2023 county averages, not school-specific. Not a measure of legal compliance. Wrong or out of date? <a href="mailto:edanmnorg@gmail.com">edanmnorg@gmail.com</a></div>`;
 card.style.display="block";
 document.getElementById('copy').onclick=()=>{{
  const link=linkFor(d.isd), out=document.getElementById('copied');
  const done=()=>{{out.textContent="Link copied.";}}, show=()=>{{out.textContent=link;}};
  if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(link).then(done,show); else show();
 }};
}}

function close(){{list.style.display="none";q.setAttribute("aria-expanded","false");q.removeAttribute("aria-activedescendant");}}
function search(){{
 const s=q.value.toLowerCase().trim(); ai=-1;
 if(!s){{close();hint.textContent=HINT;return;}}
 // Names that start with what was typed come first, then any word that starts with it.
 // Otherwise "st" lists every "...School District" before St. Cloud.
 const hay=d=>(d.name+" "+d.county+" "+d.city+" "+d.isd).toLowerCase();
 const rank=h=>h.startsWith(s)?0:h.includes(" "+s)?1:2;
 matches=D.filter(d=>hay(d).includes(s)).sort((a,b)=>rank(hay(a))-rank(hay(b))).slice(0,12);
 list.innerHTML=matches.map((d,i)=>`<div role="option" id="opt-${{i}}" data-i="${{i}}">${{d.name}} <span class="muted">&middot; ${{d.county}} County</span></div>`).join("");
 if(!matches.length){{close();hint.textContent=`No district or county matches "${{q.value.trim()}}".`;return;}}
 list.style.display="block"; q.setAttribute("aria-expanded","true"); hint.textContent=HINT;
}}
function pick(i){{
 if(!matches[i])return;
 q.value=matches[i].name; close(); render(matches[i]); remember(matches[i].isd);
 hint.textContent="Showing "+matches[i].name+".";
}}

q.addEventListener('input',search);
q.addEventListener('keydown',e=>{{
 if(list.style.display==="none")return;
 const items=[...list.children];
 if(e.key==="ArrowDown"){{ai=Math.min(ai+1,items.length-1);e.preventDefault();}}
 else if(e.key==="ArrowUp"){{ai=Math.max(ai-1,0);e.preventDefault();}}
 else if(e.key==="Enter"){{pick(ai<0?0:ai);return;}}
 else if(e.key==="Escape"){{close();return;}}
 else return;
 items.forEach((el,i)=>{{el.classList.toggle('active',i===ai);el.setAttribute("aria-selected",i===ai?"true":"false");}});
 q.setAttribute("aria-activedescendant","opt-"+ai);
 items[ai].scrollIntoView({{block:"nearest"}});
}});
list.addEventListener('click',e=>{{const d=e.target.closest('[data-i]');if(d)pick(+d.dataset.i);}});

// Open straight to a district, or to a search, when the address asks for one.
(()=>{{
 const p=new URLSearchParams(page.location.search), isd=p.get("district"), find=p.get("find");
 const d=isd&&D.find(x=>x.isd===isd);
 if(d){{q.value=d.name;render(d);hint.textContent="Showing "+d.name+".";}}
 else if(find){{q.value=find;search();if(matches.length===1)pick(0);}}
}})();
</script>
<script src="../js/embed.js"></script>
</div></body></html>"""

open(OUT, "w").write(page)
print("wrote", os.path.relpath(OUT, HERE), "with", len(rows), "districts")
# The audit file is shared on request and is no longer published with the site (October 2026).
# write_public_csv(rows)
update_reply_counts(rows)
