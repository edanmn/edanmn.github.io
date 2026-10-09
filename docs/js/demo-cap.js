/* ==========================================================================
   demo-cap.js: what a $25 monthly cap would change, for ten Minnesota plans
   and five seizure medicines. Data is window.DATA, written by build_demos.py
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
  const SOURCE = "Each carrier's 2026 Summary of Benefits and Coverage and drug list; prices from the CMS National Average Drug Acquisition Cost survey and Minnesota Medicaid";

  let drug = D.drugs.some(d => d.id === get("drug")) ? get("drug") : "epd";
  let phase = PHASE[get("when")] ? get("when") : "mid";
  let open = get("plan") == null ? -1 : +get("plan");
  if (!(open >= 0 && open < D.plans.length)) open = -1;

  const cell = (p, d) => D.cells[p + "|" + d];
  const shortPlan = (p) => p.metal ? p.carrier + " " + p.metal + (p.hsa ? " HSA" : "") : (p.hsa ? "State employees, high deductible" : "State employees");
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
    add("Today", usd(now.pays) + " a month: " + now.how);
    add("With the cap", usd(now.under) + " a month: " + now.note);
    add("On the drug list", tier(c) + (c.flags ? " (" + flags(c.flags) + ")" : ""));
    add("Price used", usd(d.price) + (/^weight/.test(d.dose) ? " for one prescription, dosed by weight. " : " for 30 days at " + d.dose + ". ") + d.basis);
    add("Plan", p.market + ". Deductible " + usd(p.ded) + ", out-of-pocket limit " + usd(p.oop) + " for one person" + (p.hsa ? ". Qualifies for a health savings account." : "."));
    add("Benefit summary", p.src);
    add("Drug list", c.fsrc);
    more.append(dl);
    return more;
  }

  function planRows(into) {
    const max = Math.max(...D.plans.map((p, i) => cell(i, drug)[phase].pays));
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

  function matrix(into) {
    const count = { lower: 0, same: 0, wait: 0, nocov: 0 }, narrow = fig.clientWidth < 560;
    const grid = h("div", "matrix");
    grid.append(h("div", "hd", ""));
    D.drugs.forEach(d => grid.append(h("div", "hd", d.name)));
    D.plans.forEach((p, i) => {
      grid.append(h("div", "rw", shortPlan(p)));
      D.drugs.forEach(d => {
        const now = cell(i, d.id)[phase];
        count[now.st]++;
        const text = now.st === "lower" ? "−" + dollars(now.save) : narrow ? { same: "=", wait: "wait", nocov: "none" }[now.st]
          : { same: "no change", wait: "waits", nocov: "not listed" }[now.st];
        const b = h("button", "cell " + now.st + (d.id === drug && i === open ? " on" : ""), text);
        b.type = "button";
        b.setAttribute("aria-label", shortPlan(p) + ", " + d.name + ": " + GROUP[now.st] + ". Today " + usd(now.pays) + ", with the cap " + usd(now.under) + ".");
        b.dataset.tip = "1";
        tip.on(b, d.name + ", " + shortPlan(p), [[usd(now.pays), "a month today"], [usd(now.under), "with the cap"], [GROUP[now.st], ""]]);
        b.addEventListener("click", () => {
          drug = d.id; open = i; set({ drug, plan: open }); render();
          const target = fig.querySelector(".pick[aria-expanded=true]");
          if (target) target.scrollIntoView({ block: "nearest", behavior: matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
        });
        grid.append(b);
      });
    });
    into.append(h("p", "small", "Of the 50 pairings " + PHASE[phase].text + ": the cap lowers the cost in " + count.lower +
      ", " + count.same + " already cost $25 or less, " + count.nocov + " are not on the plan's drug list" +
      (count.wait ? ", and " + count.wait + " wait for the deductible." : ".") + " Each box shows the monthly saving. Pick one to see how it was worked out."));
    into.append(grid);
    const key = h("ul", "legend");
    Object.keys(GROUP).forEach(k => { const li = h("li"); li.append(h("span", "chip " + k, GROUP[k])); key.append(li); });
    into.append(key);
  }

  function render() {
    tip.hide();
    const keep = fig.querySelector(".tip");
    fig.replaceChildren();
    fig.append(h("h1", "", "What would a $25 cap change?"));
    fig.append(h("p", "lede", "Two 2026 bills would have capped what a commercially insured Minnesotan pays for a seizure medicine at $25 a month. " +
      "We read the " + D.year + " benefit summary and drug list of ten Minnesota plans and worked out what five medicines cost a member today and what they would cost with the cap."));
    seg(fig, "Medicine", D.drugs.map(d => ({ id: d.id, label: d.name, sub: d.kind })), drug, (id) => { drug = id; set({ drug }); render(); });
    seg(fig, "Point in the plan year", Object.keys(PHASE).map(k => ({ id: k, label: PHASE[k].label, sub: PHASE[k].sub })), phase, (id) => { phase = id; set({ when: phase }); render(); });
    fig.append(h("h2", "", "Plan by plan"));
    fig.append(h("p", "small", "Each plan shows the monthly cost today and with the cap. Pick a plan to see the calculation and the documents it comes from."));
    planRows(fig);
    fig.append(h("h2", "", "All ten plans and five medicines"));
    matrix(fig);

    const foot = h("div", "foot");
    [
      "Sources: " + SOURCE + ".",
      "These are " + D.year + " plans. UCare's individual plans end with " + D.year + ", and most 2027 plan documents were not published when this was built.",
      "Prices are a floor. For four of the medicines we used what pharmacies pay for the drug (CMS National Average Drug Acquisition Cost, third quarter 2026). Epidiolex is outside that survey, so its price is the average Minnesota Medicaid payment per prescription in 2025. A plan's own price is usually higher, which makes coinsurance, and the saving from a cap, larger than shown.",
      "Ten plans from HealthPartners, UCare, Medica and the state employee plan. Blue Cross and Blue Shield of Minnesota and Quartz are missing because their plan-by-plan benefit summaries could not be retrieved. Self-insured employer plans are outside state insurance law and would not be covered by the cap.",
      "The bills were HF 3652 and SF 3786, which would have added epilepsy to Minn. Stat. 62Q.481. They did not pass in 2026. This page shows what the plan documents say; what one family pays depends on its own plan, dose and pharmacy.",
    ].forEach(t => foot.append(h("p", "", t)));
    fig.append(foot);
    if (keep) fig.append(keep);
  }
  render();
  // The grid of fifty shortens its words on a narrow screen.
  let wide = fig.clientWidth >= 560;
  window.addEventListener("resize", () => { const now = fig.clientWidth >= 560; if (now !== wide) { wide = now; render(); } });
})();
