#!/usr/bin/env python3
"""Build the three interactive pages in docs/sims/: the $25 cap, the district
comparison and the death certificate explorer.

Each page is a small shell holding its data as window.DATA; the drawing code is
in docs/js/demo-*.js with docs/js/demos.js and docs/css/demos.css. Reads EDAN's
working data from ../data, so it runs from the parent project.

    python3 build_demos.py
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SIMS = os.path.join(HERE, "docs", "sims")
LOOKUP = os.path.join(HERE, "docs", "find-your-district", "district_lookup.html")
VERSION = "2026-10-09j"

SHELL = """<!doctype html>
<html lang="en" data-autoheight><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="../../css/charts.css?v={v}">
<link rel="stylesheet" href="../../css/demos.css?v={v}">
</head><body>
<figure id="demo"></figure>
<noscript><p>This page needs JavaScript. The same figures are on the initiative page.</p></noscript>
<script>window.DATA = {data};</script>
<script src="../../js/demos.js?v={v}"></script>
<script src="../../js/{script}?v={v}"></script>
<script src="../../js/embed.js"></script>
</body></html>
"""


def rows(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write(folder, title, script, data):
    path = os.path.join(SIMS, folder, "main.html")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(SHELL.format(title=title, script=script, data=blob, v=VERSION))
    print("wrote", os.path.relpath(path, HERE), f"({os.path.getsize(path):,} bytes)")


# ---------------------------------------------------------------------------
# 1. The $25 cap: eight plans, the twenty most-prescribed medicines and five brands, two points in the year
# ---------------------------------------------------------------------------
# id (kept short, it goes in the page address), name shown, what kind of product it is.
DRUGS = {
    "lamotrigine 150 mg tablet (generic)": ("lam", "Lamotrigine", "generic"),
    "topiramate 100 mg tablet (generic)": ("top", "Topiramate", "generic"),
    "levetiracetam 500 mg tablet (generic)": ("lev", "Levetiracetam", "generic"),
    "divalproex ER 500 mg tablet (generic)": ("dvp", "Divalproex", "generic, extended release"),
    "oxcarbazepine 600 mg tablet (generic)": ("oxc", "Oxcarbazepine", "generic"),
    "carbamazepine ER 400 mg tablet (generic)": ("cbz", "Carbamazepine", "generic, extended release"),
    "lacosamide 150 mg tablet (generic)": ("lac", "Lacosamide", "generic"),
    "zonisamide 100 mg capsule (generic)": ("zon", "Zonisamide", "generic"),
    "phenytoin sodium extended 100 mg capsule (generic)": ("phy", "Phenytoin", "generic"),
    "primidone 250 mg tablet (generic)": ("prm", "Primidone", "generic"),
    "phenobarbital 16.2 mg tablet (generic)": ("phb", "Phenobarbital", "generic"),
    "clobazam 10 mg tablet (generic)": ("clb", "Clobazam", "generic"),
    "brivaracetam 50 mg tablet (generic)": ("brv", "Brivaracetam", "generic"),
    "ethosuximide 250 mg capsule (generic)": ("eth", "Ethosuximide", "generic"),
    "Valtoco 10 mg nasal spray (diazepam)": ("val", "Valtoco", "diazepam nasal spray, no generic"),
    "felbamate 600 mg tablet (generic)": ("fel", "Felbamate", "generic"),
    "Epidiolex oral solution (cannabidiol)": ("epd", "Epidiolex", "cannabidiol, no generic"),
    "Xcopri 200 mg tablet (cenobamate)": ("xcp", "Xcopri", "cenobamate, no generic"),
    "Nayzilam 5 mg nasal spray (midazolam)": ("nay", "Nayzilam", "midazolam nasal spray, no generic"),
    "perampanel 8 mg tablet (generic)": ("per", "Perampanel", "generic"),
    "Onfi 10 mg tablet (brand clobazam)": ("onfi", "Onfi", "brand of clobazam"),
    "Fintepla oral solution (fenfluramine)": ("fin", "Fintepla", "fenfluramine, no generic"),
    "Diacomit (stiripentol)": ("dia", "Diacomit", "stiripentol, no generic"),
    "Sabril (brand vigabatrin)": ("sab", "Sabril", "brand of vigabatrin"),
    "Aptiom 800 mg tablet (brand eslicarbazepine)": ("apt", "Aptiom", "brand of eslicarbazepine"),
}
# Priced as one prescription rather than thirty days of tablets.
PER_FILL = {"epd": "dosed by weight", "fin": "dosed by weight", "dia": "dosed by weight", "sab": "dosed by weight",
            "val": "one carton of two devices", "nay": "one carton of two devices"}
PHASES = {"January, deductible not met": "jan", "mid-year, deductible met": "mid"}
CARRIER = {"healthpartners": "HealthPartners", "ucare": "UCare", "medica": "Medica"}


def money(s):
    return round(float(s), 2)


def cap_status(r):
    """Which of four things the cap does for this plan, drug and point in the year."""
    if r["covered"] != "yes":
        return "nocov"
    if money(r["monthly_saving_usd"]) > 0:
        return "lower"
    if r["cap_note"].startswith("the cap does not apply yet") and money(r["member_pays_usd"]) > 25:
        return "wait"
    return "same"


def no_paths(text):
    """Source notes name carrier documents; drop any pointer to EDAN's own files."""
    return re.sub(r"data/\S+", "EDAN price file", text)


def build_cap():
    src = rows("mn_plan_cost_sharing.csv")
    plans, drugs, cells, seen = [], [], {}, {}
    for r in src:
        pid = seen.get(r["plan"])
        if pid is None:
            plans.append({
                "name": r["plan"],
                "carrier": CARRIER[r["carrier"]],
                "market": "Individual market",
                "metal": r["metal"],
                "hsa": r["hsa_qualified"] == "yes",
                "ded": money(r["deductible_single"]),
                "oop": money(r["oop_max_single"]),
                "src": no_paths(r["plan_source"]),
            })
            pid = seen[r["plan"]] = len(plans) - 1
        did, short, kind = DRUGS[r["drug"]]
        if not any(d["id"] == did for d in drugs):
            drugs.append({"id": did, "name": short, "kind": kind, "full": r["drug"],
                          "dose": PER_FILL.get(did, r["dose"]), "fill": did in PER_FILL,
                          "dose_src": r["dose_source"],
                          "rank": int(r["commercial_rx_rank"]) if r["commercial_rx_rank"] else None,
                          "price": money(r["thirty_day_price_basis_usd"]),
                          "basis": r["price_basis"].replace("NOT NADAC", "Not NADAC")})
        cell = cells.setdefault(f"{pid}|{did}", {
            "tier": r["formulary_tier"], "flags": r["formulary_flags"], "covered": r["covered"] == "yes",
            "fsrc": no_paths(r["formulary_source"]),
        })
        cell[PHASES[r["phase"]]] = {
            "pays": money(r["member_pays_usd"]), "how": r["how_calculated"],
            "under": money(r["member_pays_under_hf3652_usd"]), "save": money(r["monthly_saving_usd"]),
            "note": r["cap_note"], "st": cap_status(r),
        }
    drugs.sort(key=lambda d: d["rank"] or 99)
    assert len(plans) == 8 and len(drugs) == 25 and len(cells) == 200
    assert [d["rank"] for d in drugs] == list(range(1, 21)) + [None] * 5
    rank_year = {r["commercial_rx_year"] for r in src if r["commercial_rx_year"]}
    assert rank_year == {"2022"}
    write("cap-calculator", "What would a $25 cap change? Eight Minnesota plans, twenty-five seizure medicines",
          "demo-cap.js", {"plans": plans, "drugs": drugs, "cells": cells, "year": 2026, "rank_year": 2022})


# ---------------------------------------------------------------------------
# 2. District comparison
# ---------------------------------------------------------------------------
CLS = {"FOUND_SEIZURE_SPECIFIC": "posted", "FOUND_MED_POLICY_ONLY": "med",
       "NOT_FOUND": "nothing", "NOT_VERIFIABLE": "nocheck"}


def build_districts():
    # The lookup page already holds the audit as published; take the public fields from it.
    html = open(LOOKUP, encoding="utf-8").read()
    full = json.loads(re.search(r"(?:const|var|let)\s+\w+\s*=\s*(\[\{.*?\}\]);", html, re.S).group(1))
    out = []
    for d in full:
        cls = CLS[d["cls"]]
        out.append([d["isd"], d["name"], d["county"], d["city"], d["type"],
                    int(float(d["enroll"] or 0)), cls,
                    d["url"] if cls == "posted" else ""])
    assert len(out) == 329
    posted = sum(1 for d in out if d[6] == "posted")
    write("district-compare", "How does your district compare? Seizure plans in similar Minnesota districts",
          "demo-districts.js", {"d": out, "checked": "June 2026", "posted": posted})


# ---------------------------------------------------------------------------
# 3. Death certificates
# ---------------------------------------------------------------------------
def n(s):
    s = (s or "").replace(",", "").strip()
    return int(s) if s.isdigit() else None        # None is a suppressed count, fewer than 10


def rate(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def table(name):
    return [{"g": r["group"], "n": n(r["deaths"]), "r": rate(r["crude_rate_per_100k"]), "ci": r["ci_95"]}
            for r in rows(name) if r["group"] != "Total" and "Urbanization" not in r["group"]]


def build_deaths():
    defs = {"any": "mcd_any", "epi": "mcd_epilepsy", "ucd": "ucd_epilepsy"}
    year = {k: table(f"mn_epilepsy_mortality_{v}_by_year.csv") for k, v in defs.items()}
    age = {k: table(f"mn_epilepsy_mortality_{v}_by_age10.csv") for k, v in defs.items()}
    total = {k: sum(r["n"] for r in year[k]) for k in defs}
    assert total == {"any": 6077, "epi": 1404, "ucd": 415}

    # CDC withholds counts under 10, and a withheld count must not be recoverable by subtracting
    # the bars from a total. For the underlying cause the two youngest groups are withheld, and
    # the place-of-death view gives a total for ages 1 to 44, so the ages are regrouped across
    # both boundaries: nothing shown here can be subtracted down to one withheld group.
    src = [r for r in rows("mn_epilepsy_mortality_ucd_epilepsy_by_age10.csv") if r["group"] != "Total"]
    assert [r["deaths"] for r in src[:2]] == ["Suppressed", "Suppressed"] and len(src) == 11
    pop = lambda rs: sum(int(r["population"].replace(",", "")) for r in rs)
    older = sum(int(r["deaths"]) for r in src[4:])
    merged = [("Under 25 years", total["ucd"] - older, src[:4]),
              ("25-54 years", sum(int(r["deaths"]) for r in src[4:7]), src[4:7])]
    age["ucd"] = [{"g": g, "n": d, "r": round(d / pop(rs) * 1e5, 1), "ci": ""} for g, d, rs in merged] + age["ucd"][7:]
    assert sum(r["n"] for r in age["ucd"]) == total["ucd"] and all(r["n"] >= 10 for r in age["ucd"])

    place = {}
    for r in rows("mn_epilepsy_mortality_place_of_death.csv"):
        key = ("ucd" if r["cause"].startswith("underlying") else "epi") + ("_young" if "1-44" in r["age_scope"] else "_all")
        if r["place_of_death"] != "Total":
            place.setdefault(key, {"total": int(r["total_deaths"]), "rows": []})["rows"].append(
                {"g": r["place_of_death"], "n": n(r["deaths"])})
    # Same rule for places: withheld places are folded into "Other", so that the bars add up to
    # the total and no withheld count can be found by subtraction.
    for p in place.values():
        keep = [r for r in p["rows"] if r["n"] is not None and r["g"] != "Other"]
        rest = p["total"] - sum(r["n"] for r in keep)
        assert rest >= 10, rest
        p["rows"] = keep + [{"g": "Other", "n": rest}]

    states = [{"g": r["area"], "n": int(r["deaths"]), "r": float(r["age_adjusted_rate_per_100k"]),
               "ci": r["age_adjusted_ci_95"]} for r in rows("epilepsy_mortality_neighbor_states.csv")]

    # SUDEP written on the certificate (MDH). Single years and single codes have cells of 1,
    # so only multi-year totals leave this script.
    named = [(int(r["year"]), r["decd_agegrp"], r["unly_icd"], int(r["count"]))
             for r in rows("mdh_chs_sudep_text_deaths_2011_2024.csv")]
    span = lambda a, b: sum(c for y, _, _, c in named if a <= y <= b)
    all_named = span(2011, 2024)
    under45 = sum(c for _, a, _, c in named if a in ("Ages under 15", "Ages 15-24", "Ages 25-44"))
    as_epilepsy = sum(c for _, _, icd, c in named if icd.startswith("G40"))
    assert (all_named, under45, as_epilepsy) == (74, 63, 60)
    sudep = {
        "periods": [["2011 to 2015", span(2011, 2015)], ["2016 to 2019", span(2016, 2019)], ["2020 to 2024", span(2020, 2024)]],
        "total": all_named, "under45": under45, "as_epilepsy": as_epilepsy,
        "same_years": span(2018, 2024),
    }
    assert [p[1] for p in sudep["periods"]] == [8, 23, 43]

    # SUDEP deaths expected from published rates: people with active epilepsy (CDC, Zack and
    # Kobau, MMWR 2017, estimate for 2015) times the rate per 1,000 a year (Harden et al.,
    # Neurology 2017, AAN/AES guideline). Each rate is [estimate, low, high] of its 95% interval.
    people = {"adults": 46300, "children": 7400}
    rate = {"adults": [1.2, 0.64, 2.32], "children": [0.22, 0.16, 0.31]}
    assert sum(people.values()) == 53700
    exp = {k: [people[k] * r / 1000 for r in rate[k]] for k in people}
    both = [round(exp["adults"][i] + exp["children"][i]) for i in range(3)]
    assert both == [57, 31, 110]
    last = sudep["periods"][-1]
    assert last == ["2020 to 2024", 43]
    expected = {
        "people": people, "rate": rate,
        "each": {k: [round(v) for v in exp[k]] for k in exp},
        "year": both, "named_period": last[0], "named": last[1], "named_years": 5,
        "ucd_year": round(total["ucd"] / 7),
    }
    assert expected["ucd_year"] == 59

    write("death-certificates", "What Minnesota death certificates record about epilepsy, 2018 to 2024",
          "demo-deaths.js", {"year": year, "age": age, "total": total, "place": place,
                             "states": states, "sudep": sudep, "expected": expected})


if __name__ == "__main__":
    build_cap()
    build_districts()
    build_deaths()
