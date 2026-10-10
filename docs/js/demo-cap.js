/* ==========================================================================
   demo-cap.js: what a $25 monthly cap would change, for eight Minnesota plans
   and the twenty seizure medicines most prescribed to commercially insured
   Minnesotans (plus five costly brands). Data is window.DATA, written by build_demos.py
   from each carrier's 2026 benefit summary and drug list.

   Every plan and medicine pairing lands in one of four groups:
     lower  the cap lowers what the member pays
     same   the member already pays $25 or less
     wait   a high-deductible plan with a health savings account: the cap waits
            until the deductible is met
     nocov  the medicine is not on the plan's drug list, so there is no cost
            sharing for a cap to limit
   ========================================================================== */
(function () {
  "use strict";
  const { h, usd, get, set, seg, tips } = window.EDAN;
  const D = window.DATA, fig = document.getElementById("demo");
  const tip = tips(fig);

  const GROUP = {
    lower: "Cap lowers the cost",
    same: "Already $25 or less",
    wait: "Cap waits for the deductible",
    nocov: "Not on the drug list",
  };
  const PHASE = {
    jan: { label: "January", sub: "before the deductible is met", text: "in January, before the deductible is met" },
    mid: { label: "Mid-year", sub: "after the deductible is met", text: "at mid-year, after the deductible is met" },
  };
  const SOURCE = "Each carrier's 2026 Summary of Benefits and Coverage and drug list; prices from the CMS National Average Drug Acquisition Cost survey and Minnesota Medicaid; ranking from the Minnesota All Payer Claims Database public use file, " + D.rank_year;
  const TOTAL = D.plans.length * D.drugs.length;
  const each = (d) => d.fill ? "a fill" : "a month";

  let drug = D.drugs.some(d => d.id === get("drug")) ? get("drug") : D.drugs[0].id;
  let phase = PHASE[get("when")] ? get("when") : "mid";
  let open = get("plan") == null ? -1 : +get("plan");
  if (!(open >= 0 && open < D.plans.length)) open = -1;

  const cell = (p, d) => D.cells[p + "|" + d];
  const shortPlan = (p) => p.carrier + " " + p.metal + (p.hsa ? " HSA" : "");
  const dollars = (v) => usd(Math.round(v));

  function tier(c) {
    if (c.tier === "NF") return "Marked non-formulary, which the plan treats as not covered";
    if (c.tier === "absent") return "Not named anywhere in the drug list";
    return "Tier " + c.tier;
  }
  function flags(text) {
    return text.replace(/\bPA\b/g, "prior authorization").replace(/\bQL\b/g, "quantity limit")
      .replace(/\bSP\b/g, "specialty pharmacy").replace(/\bEDS\b(?! \()/g, "extended day supply");
  }

  function details(i) {
    const p = D.plans[i], d = D.drugs.find(x => x.id === drug), c = cell(i, drug), now = c[phase];
    const more = h("div", "more panel"), dl = h("dl");
    const add = (k, v) => { if (v) dl.append(h("dt", "", k), h("dd", "", v)); };
    add("Today", usd(now.pays) + " " + each(d) + ": " + now.how);
    add("With the cap", usd(now.under) + " " + each(d) + ": " + now.note);
    add("On the drug list", tier(c) + (c.flags ? " (" + flags(c.flags) + ")" : ""));
    add("Price used", usd(d.price) + (d.fill ? " for one prescription, " + d.dose + ". " : " for 30 days at " + d.dose + ". ") + d.basis);
    add("Dose from", d.dose_src);
    add("Plan", p.market + ". Deductible " + usd(p.ded) + ", out-of-pocket limit " + usd(p.oop) + " for one person" + (p.hsa ? ". Qualifies for a health savings account." : "."));
    add("Benefit summary", p.src);
    add("Drug list", c.fsrc);
    more.append(dl);
    return more;
  }

  function planRows(into) {
    const max = Math.max(...D.plans.map((p, i) => cell(i, drug)[phase].pays)), d = D.drugs.find(x => x.id === drug);
    const wrap = h("div", "plans");
    D.plans.forEach((p, i) => {
      const now = cell(i, drug)[phase];
      const box = h("div", "plan"), b = h("button", "pick");
      b.type = "button"; b.setAttribute("aria-expanded", open === i ? "true" : "false");
      const nm = h("span", "nm", p.name);
      nm.append(h("small", "", [p.carrier, p.metal, usd(p.ded) + " deductible"].filter(Boolean).join(" · ")));
      const pair = h("span", "pair");
      [["Today", now.pays, ""], ["With the cap", now.under, now.st === "lower" ? "after" : "flat"]].forEach(([lab, v, cls]) => {
        const line = h("div", cls), bar = h("i"), txt = h("span");
        bar.style.width = "calc((100% - 10.5em) * " + (max ? v / max : 0).toFixed(4) + ")";
        txt.append(usd(v) + " ", h("em", "", lab.toLowerCase()));
        line.append(bar, txt);
        pair.append(line);
      });
      b.append(nm, pair, h("span", "chip " + now.st, GROUP[now.st]));
      b.addEventListener("click", () => { open = open === i ? -1 : i; set({ plan: open < 0 ? null : open }); render(); });
      box.append(b);
      if (open === i) box.append(details(i));
      wrap.append(box);
    });
    into.append(wrap);
  }

  // Every medicine in one list: eight squares a row, one for each plan in the order shown above.
  function overview(into) {
    const count = { lower: 0, same: 0, wait: 0, nocov: 0 };
    const list = h("div", "meds");
    D.drugs.forEach(d => {
      const row = h("div", "med" + (d.id === drug ? " on" : "")), name = h("button", "nm", d.name);
      name.type = "button";
      name.append(h("small", "", d.kind));
      name.addEventListener("click", () => { drug = d.id; open = -1; set({ drug, plan: null }); render(); fig.querySelector("select").focus(); });
      const squares = h("div", "grid");
      let lower = 0;
      D.plans.forEach((p, i) => {
        const now = cell(i, d.id)[phase];
        count[now.st]++;
        if (now.st === "lower") lower++;
        const b = h("button", "sq " + now.st + (d.id === drug && i === open ? " me" : ""));
        b.type = "button";
        b.setAttribute("aria-label", d.name + ", " + shortPlan(p) + ": " + GROUP[now.st] + ". Today " + usd(now.pays) + ", with the cap " + usd(now.under) + ".");
        tip.on(b, d.name + ", " + shortPlan(p), [[usd(now.pays), each(d) + " today"], [usd(now.under), "with the cap"], [GROUP[now.st], ""]]);
        b.addEventListener("click", () => {
          drug = d.id; open = i; set({ drug, plan: open }); render();
          const target = fig.querySelector(".pick[aria-expanded=true]");
          if (target) target.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
        });
        squares.append(b);
      });
      row.append(name, squares, h("span", "n", lower ? "lower on " + lower : "no change"));
      list.append(row);
    });
    into.append(h("p", "small", "Each row is one medicine and each square is one plan, in the order of the list above. Of the " + TOTAL + " pairings " + PHASE[phase].text +
      ": the cap lowers the cost in " + count.lower + ", " + count.same + " already cost $25 or less, " + count.nocov + " are not on the plan's drug list" +
      (count.wait ? ", and " + count.wait + " wait for the deductible." : ".") + " Pick a square to see how it was worked out."));
    const key = h("ul", "legend");
    Object.keys(GROUP).forEach(k => { const li = h("li"); li.append(h("span", "chip " + k, GROUP[k])); key.append(li); });
    into.append(key, list);
  }

  // The medicine picker: a list in order of use, too long for a row of buttons.
  function picker(into) {
    const wrap = h("div", "ctl"), label = h("label", "", "Medicine"), sel = h("select");
    sel.id = "medicine"; label.htmlFor = sel.id;
    const top = h("optgroup"), more = h("optgroup");
    top.label = "Twenty most prescribed, in order"; more.label = "Also priced";
    D.drugs.forEach(d => {
      const o = h("option", "", d.name + " (" + d.kind + ")");
      o.value = d.id; o.selected = d.id === drug;
      (d.rank ? top : more).append(o);
    });
    sel.append(top, more);
    sel.addEventListener("change", () => { drug = sel.value; open = -1; set({ drug, plan: null }); render(); fig.querySelector("select").focus(); });
    wrap.append(label, sel);
    into.append(wrap);
  }

  function render() {
    tip.hide();
    const keep = fig.querySelector(".tip");
    fig.replaceChildren();
    fig.append(h("h1", "", "What would a $25 cap change?"));
    fig.append(h("p", "lede", "Two 2026 bills would have capped what a commercially insured Minnesotan pays for a seizure medicine at $25 a month. " +
      "We read the " + D.year + " benefit summary and drug list of eight Minnesota plans and worked out what the twenty most prescribed seizure medicines, and five costly brands, cost a member today and what they would cost with the cap."));
    picker(fig);
    seg(fig, "Point in the plan year", Object.keys(PHASE).map(k => ({ id: k, label: PHASE[k].label, sub: PHASE[k].sub })), phase, (id) => { phase = id; set({ when: phase }); render(); });
    const chosen = D.drugs.find(d => d.id === drug);
    fig.append(h("h2", "", chosen.name + ", plan by plan"));
    fig.append(h("p", "small", "Each plan shows the cost of " + (chosen.fill ? "one prescription (" + chosen.dose + ")" : "30 days at " + chosen.dose) + ", today and with the cap. Pick a plan to see the calculation and the documents it comes from."));
    planRows(fig);
    fig.append(h("h2", "", "Every medicine across the eight plans"));
    overview(fig);

    const foot = h("div", "foot");
    [
      "Sources: " + SOURCE + ".",
      "The twenty medicines are those with the most prescriptions filled by commercially insured Minnesotans in " + D.rank_year + ", the newest year the state has published, counted by active ingredient. The count covers every use of a medicine, so topiramate's includes migraine and lamotrigine's includes bipolar disorder. Gabapentin, pregabalin and clonazepam are left out because most of their use is for other conditions. Five brands are also priced. Fintepla, Diacomit, Sabril and Aptiom each cost Minnesota Medicaid more than $1,800 a prescription in 2025, and Onfi is the brand of clobazam. They are examples; other costly brands, such as Ztalmy, are not priced here. Sabril, Aptiom and Onfi each have a generic, and where a drug list carries the medicine it carries the generic.",
      "One product stands for each medicine: a common strength at a dose from its FDA label, in the generic form where one exists. Other strengths, forms and brands of the same medicine can sit on a different tier. Valtoco and Nayzilam are rescue medicines, priced as one carton and not as a month's supply.",
      "Only plans whose drug list is public are shown, and every tier is read from the carrier's own list. Minnesota's state employee plan is left out because its drug tiers sit behind a member login.",
      "These are " + D.year + " plans. UCare's individual plans end with " + D.year + ", and most 2027 plan documents were not published when this was built.",
      "Prices are a floor. For most medicines we used what pharmacies pay for the drug (CMS National Average Drug Acquisition Cost, third quarter 2026). Epidiolex, Fintepla, Diacomit and Sabril are outside that survey, so each is priced at the average Minnesota Medicaid payment per prescription in 2025, before rebates. A plan's own price is usually higher, which makes coinsurance, and the saving from a cap, larger than shown.",
      "Eight individual-market plans from HealthPartners, UCare and Medica, with drug lists dated October 2026. Blue Cross and Blue Shield of Minnesota and Quartz are missing because their plan-by-plan benefit summaries could not be retrieved. Self-insured employer plans are outside state insurance law and would not be covered by the cap.",
      "The bills were HF 3652 and SF 3786, which would have added epilepsy to Minn. Stat. 62Q.481. They did not pass in 2026. This page shows what the plan documents say; what one family pays depends on its own plan, dose and pharmacy.",
    ].forEach(t => foot.append(h("p", "", t)));
    fig.append(foot);
    if (keep) fig.append(keep);
  }
  render();
})();
