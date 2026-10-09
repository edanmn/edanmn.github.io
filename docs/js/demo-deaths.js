/* ==========================================================================
   demo-deaths.js: what Minnesota death certificates record about epilepsy.
   Data is window.DATA, written by build_demos.py from CDC WONDER (coded causes,
   2018 to 2024) and a Minnesota Department of Health search of certificate text
   for SUDEP (2011 to 2024).

   Three ways of counting come from the coded files:
     any  epilepsy or seizures mentioned anywhere (G40, G41 or R56)
     epi  epilepsy mentioned anywhere (G40 or G41)
     ucd  epilepsy as the underlying cause
   A count of null was withheld by CDC because it is between 1 and 9.
   SUDEP has no code, so it appears only in the text search, in multi-year totals.
   One view sets the named count beside the number expected from published rates.
   ========================================================================== */
(function () {
  "use strict";
  const { h, num, pct, get, set, seg, tips } = window.EDAN;
  const D = window.DATA, fig = document.getElementById("demo");
  const tip = tips(fig);

  const CDC = "CDC WONDER, Multiple Cause of Death, Minnesota residents, 2018 to 2024";
  const RATES = "CDC, estimate of Minnesotans with active epilepsy in 2015 (Zack and Kobau, MMWR 2017); American Academy of Neurology and American Epilepsy Society guideline on SUDEP rates (Harden and others, Neurology 2017)";
  const MDH = "Minnesota Department of Health, Minnesota Center for Health Statistics, death certificate data, custom tabulation for EDAN, October 2026";
  const DEF = {
    any: { label: "Epilepsy or seizures mentioned", sub: "G40, G41 or R56", said: "mentioned epilepsy or seizures",
      long: "Any of the codes G40 (epilepsy), G41 (status epilepticus) or R56 (convulsions) anywhere on the certificate. R56 takes in seizures recorded without an epilepsy diagnosis, so this is the widest count." },
    epi: { label: "Epilepsy mentioned", sub: "G40 or G41", said: "mentioned epilepsy",
      long: "G40 or G41 anywhere on the certificate, whether as the underlying cause or as a contributing one." },
    ucd: { label: "Epilepsy as the underlying cause", sub: "G40 or G41", said: "gave epilepsy as the underlying cause",
      long: "G40 or G41 chosen as the single underlying cause of death, the condition that started the chain of events." },
  };
  const VIEWS = [["count", "The count"], ["year", "By year"], ["age", "By age"], ["place", "Where people died"], ["named", "SUDEP by name"], ["expected", "Expected and named"], ["states", "Other states"]];
  const SCOPE = {
    epi_all: { label: "Epilepsy mentioned", sub: "all ages", who: "Minnesotans whose death certificate mentioned epilepsy" },
    epi_young: { label: "Epilepsy mentioned", sub: "ages 1 to 44", who: "Minnesotans aged 1 to 44 whose death certificate mentioned epilepsy" },
    ucd_young: { label: "Epilepsy the underlying cause", sub: "ages 1 to 44", who: "Minnesotans aged 1 to 44 whose death certificate gave epilepsy as the underlying cause" },
  };
  const PLACE = {
    "Decedent's home": "At home", "Medical Facility - Inpatient": "Hospital, inpatient",
    "Medical Facility - Outpatient or ER": "Hospital, outpatient or emergency room",
    "Medical Facility - Dead on Arrival": "Dead on arrival at a hospital", "Hospice facility": "Hospice",
    "Nursing home/long term care": "Nursing home or long-term care", "Other": "Somewhere else", "Place of death unknown": "Not recorded",
  };
  const ageName = (g) => g === "< 1 year" ? "Under 1" : g === "85+ years" ? "85 and over" : g.replace(" years", "").replace("-", " to ");

  let view = VIEWS.some(v => v[0] === get("show")) ? get("show") : "count";
  let def = DEF[get("count")] ? get("count") : "epi";
  let measure = get("as") === "rate" ? "rate" : "deaths";
  let scope = SCOPE[get("who")] ? get("who") : "ucd_young";

  /* ---- Bars and columns, in the charts' own markup ---- */
  function bars(into, rows, axis) {
    const max = Math.max(...rows.map(r => r.value || 0));
    const room = (Math.max(...rows.map(r => (r.text + (r.extra || "")).length)) + 2) * 0.56;
    const wrap = h("div", "bars");
    rows.forEach(r => {
      const row = h("div", "row" + (r.sel ? " sel" : "") + (r.pick ? " pickable" : "")), track = h("div", "track");
      const bar = h("div", "bar" + (r.tone ? " " + r.tone : ""));
      bar.style.width = r.value ? "calc((100% - " + room.toFixed(2) + "em) * " + (r.value / max).toFixed(4) + ")" : "0";
      if (!r.value) bar.style.minWidth = "0";
      track.append(bar, h("span", "val", r.text));
      if (r.extra) track.append(h("span", "ci", r.extra));
      const lab = h("div", "lab", r.label);
      if (r.sub) lab.append(h("small", "", " " + r.sub));
      row.append(lab, track);
      if (r.tip) tip.on(row, r.label, r.tip);
      if (r.pick) {
        row.tabIndex = 0; row.setAttribute("role", "button");
        row.addEventListener("click", r.pick);
        row.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); r.pick(); } });
      }
      wrap.append(row);
    });
    into.append(wrap);
    if (axis) into.append(h("p", "axis", axis));
  }
  function columns(into, cols, yTitle) {
    if (cols.length * 56 > fig.clientWidth) return bars(into, cols.map(c => ({ label: c.label, value: c.value, text: c.text, tip: c.tip })), yTitle);
    const top = niceTop(Math.max(...cols.map(c => c.value)));
    const wrap = h("div", "cols"), ticks = h("div", "ticks"), plot = h("div", "plot"), labs = h("div", "labs");
    wrap.append(h("div", "ytitle", yTitle));
    for (let i = 0; i <= 4; i++) {
      const t = top / 4 * i, lab = h("span", "", num(t));
      lab.style.bottom = i * 25 + "%"; ticks.append(lab);
      if (i) { const line = h("i"); line.style.bottom = i * 25 + "%"; plot.append(line); }
    }
    cols.forEach(c => {
      const col = h("div", "col"), bar = h("div", "bar"), cap = h("div", "cap", c.text), p = c.value / top * 100 + "%";
      bar.style.height = p; cap.style.bottom = p;
      col.append(bar, cap);
      if (c.tip) tip.on(col, c.label, c.tip);
      plot.append(col);
      labs.append(h("span", "", c.label));
    });
    wrap.append(ticks, plot, labs);
    into.append(wrap);
  }
  function niceTop(max) {
    const raw = max / 4, p = Math.pow(10, Math.floor(Math.log10(raw))), m = raw / p;
    return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 5 ? 5 : 10) * p * 4;
  }
  const note = (into, text) => into.append(h("p", "small", text));
  function defPicker(into) {
    seg(into, "Which deaths to count", Object.keys(DEF).map(k => ({ id: k, label: DEF[k].label, sub: DEF[k].sub })), def, (id) => { def = id; set({ count: def }); render(); });
    note(into, DEF[def].long);
  }

  /* ---- The views ---- */
  function count(into) {
    const t = D.total, s = D.sudep;
    const go = (k) => () => { def = k; view = "year"; set({ count: def, show: view }); render(); };
    bars(into, Object.keys(DEF).map(k => ({
      label: DEF[k].label, sub: "(" + DEF[k].sub + ")", value: t[k], text: num(t[k]), extra: "about " + num(Math.round(t[k] / 7 / 5) * 5) + " a year",
      tip: [[num(t[k]), "deaths, 2018 to 2024"], ["", DEF[k].long]], pick: go(k),
    })).concat([{
      label: "SUDEP written in words", sub: "(no code exists)", value: s.same_years, text: String(s.same_years), extra: "about " + Math.round(s.same_years / 7) + " a year", tone: "alt",
      tip: [[s.same_years, "certificates, 2018 to 2024"], ["", "Found by searching the cause-of-death text."]],
      pick: () => { view = "named"; set({ show: view }); render(); },
    }]), "Minnesota death certificates, 2018 to 2024");
    note(into, "Each count sits inside the one above it, except the last. SUDEP has no diagnostic code, so the coded files cannot count it. " +
      "The Minnesota Department of Health found these certificates by searching the written cause of death. Some of them carry a different underlying cause, " +
      "so they are not all among the " + num(t.ucd) + ". Pick a row to see it by year.");
  }

  function year(into) {
    defPicker(into);
    const rows = D.year[def];
    columns(into, rows.map(r => ({ label: r.g, value: r.n, text: num(r.n),
      tip: [[num(r.n), "deaths"], [r.r, "per 100,000 residents"], [r.ci, "95% confidence interval"]] })), "Deaths a year");
  }

  function age(into) {
    defPicker(into);
    seg(into, "Show", [{ id: "deaths", label: "Number of deaths" }, { id: "rate", label: "Deaths per 100,000 residents" }], measure,
      (id) => { measure = id; set({ as: measure === "rate" ? "rate" : null }); render(); });
    const rows = D.age[def];
    bars(into, rows.map(r => {
      const v = measure === "rate" ? r.r : r.n;
      return { label: ageName(r.g), value: v, text: v == null ? "fewer than 10 deaths" : measure === "rate" ? String(v) : num(v),
        extra: measure === "rate" && r.ci ? r.ci.replace(" - ", " to ") : "",
        tip: r.n == null ? [["1 to 9", "deaths, withheld by CDC"]] : [[num(r.n), "deaths, 2018 to 2024"], [r.r, "per 100,000 residents a year"], [r.ci.replace(" - ", " to "), "95% confidence interval"]] };
    }), measure === "rate" ? "Deaths per 100,000 residents a year, with the 95% confidence interval" : "Deaths, 2018 to 2024");
  }

  function place(into) {
    seg(into, "Whose deaths", Object.keys(SCOPE).map(k => ({ id: k, label: SCOPE[k].label, sub: SCOPE[k].sub })), scope, (id) => { scope = id; set({ who: scope }); render(); });
    const p = D.place[scope];
    bars(into, p.rows.slice().sort((a, b) => (b.n || 0) - (a.n || 0)).map(r => ({
      label: PLACE[r.g] || r.g, value: r.n, text: r.n == null ? "fewer than 10" : num(r.n), extra: r.n == null ? "" : pct(r.n, p.total),
      tone: r.g === "Decedent's home" ? "" : "off", sel: r.g === "Decedent's home",
      tip: r.n == null ? [["1 to 9", "deaths, withheld by CDC"]] : [[num(r.n), "of " + num(p.total) + " deaths"], [pct(r.n, p.total), "of this group"]],
    })), "Deaths, 2018 to 2024");
    note(into, "The coded files do not record whether anyone was present or whether the person was asleep. Place of death is the closest public measure. Dying at home is not proof of SUDEP, and some SUDEP deaths happen elsewhere.");
  }

  function named(into) {
    const s = D.sudep, p = s.periods;
    columns(into, p.map(x => ({ label: x[0], value: x[1], text: String(x[1]), tip: [[x[1], "certificates that name SUDEP"]] })), "Certificates that name SUDEP");
    const big = h("div", "big");
    [[s.total, "certificates in 14 years"], [s.under45, "of them for people under 45"], [s.as_epilepsy, "kept an epilepsy code as the underlying cause"],
     [s.total - s.as_epilepsy, "were coded to another condition"]].forEach(([v, label]) => { const b = h("div"); b.append(h("b", "", String(v)), h("span", "", label)); big.append(b); });
    into.append(big);
    note(into, "The department searched for SUDEP and its spelled-out forms. The three periods are not the same length: five, four and five years.");
    note(into, "This is a count of certificates, which is different from a count of SUDEP deaths. A death certificate is the certifier's opinion from the information available at the time. " +
      "The numbers cannot show how many SUDEP deaths went unnamed, or why. The rise across the periods is consistent with medical examiners following the 2018 recommendations of the National Association of Medical Examiners on naming SUDEP, and may not reflect any change in how often it happens.");
    note(into, "The " + (s.total - s.as_epilepsy) + " coded to another condition, such as a brain malformation or cerebral palsy, would be missed by a count built on epilepsy codes alone.");
  }

  function expected(into) {
    const e = D.expected, per = Math.round(e.named / e.named_years), y = e.year;
    // On a narrow screen the notes beside each bar move to the hover card and the table, so the bars keep their room.
    const narrow = fig.clientWidth < 560;
    bars(into, [
      { label: "Expected from published rates", sub: "(an estimate)", value: y[0], text: "about " + y[0] + " a year", extra: narrow ? "" : "range " + y[1] + " to " + y[2], tone: "off",
        tip: [[y[0], "a year, at the guideline's rates"], [y[1] + " to " + y[2], "if both rates sit at the low or the high end of their 95% confidence intervals"]] },
      { label: "Certificates that name SUDEP", sub: "(" + e.named_period + ")", value: per, text: "about " + per + " a year", extra: narrow ? "" : e.named + " in " + e.named_years + " years", sel: true,
        tip: [[e.named, "certificates, " + e.named_period], ["", "Found by the Minnesota Department of Health in the written cause of death."]],
        pick: () => { view = "named"; set({ show: view }); render(); } },
      { label: "Epilepsy as the underlying cause", sub: "(every age and kind of death)", value: e.ucd_year, text: "about " + e.ucd_year + " a year", extra: narrow ? "" : num(D.total.ucd) + " in 7 years", tone: "off",
        tip: [[num(D.total.ucd), "deaths, 2018 to 2024"], ["", "Includes deaths in hospitals and nursing homes and deaths from status epilepticus. Most are probably not SUDEP."]],
        pick: () => { def = "ucd"; view = "year"; set({ count: def, show: view }); render(); } },
    ], "Deaths a year in Minnesota");
    note(into, "The expected number is an estimate, and Minnesota's own rate has never been measured. The difference between the first two bars is not a count of missed SUDEP deaths.");

    into.append(h("h2", "", "How the estimate is worked out"));
    const wrap = h("div", "workwrap"), table = h("table", "work"), head = h("tr"), body = h("tbody");
    ["", "Minnesotans with active epilepsy", "SUDEP deaths per 1,000 a year", "Expected a year"].forEach((t, i) => { const th = h("th", "", t); if (i) th.className = "n"; head.append(th); });
    const thead = h("thead"); thead.append(head); table.append(thead, body);
    const line = (name, people, rate, out, cls) => {
      const tr = h("tr", cls || "");
      tr.append(h("th", "", name), h("td", "n", people), h("td", "n", rate), h("td", "n", out));
      body.append(tr);
    };
    [["adults", "Adults"], ["children", "Children under 18"]].forEach(([k, name]) => {
      const r = e.rate[k], x = e.each[k];
      line(name, num(e.people[k]), r[0] + " (" + r[1] + " to " + r[2] + ")", x[0] + " (" + x[1] + " to " + x[2] + ")");
    });
    line("Together", num(e.people.adults + e.people.children), "", y[0] + " (" + y[1] + " to " + y[2] + ")", "sum");
    wrap.append(table); into.append(wrap);
    note(into, "The numbers in brackets are the 95% confidence interval of each rate. Each line is rounded on its own, so the two lines can differ from the total by one.");

    into.append(h("h2", "", "What this comparison cannot show"));
    const limits = h("ul", "limits");
    [
      "The expected number is an estimate. The rates come from studies in other places, pooled in a 2017 guideline, and the guideline calls them uncertain. The count of people is a CDC estimate for 2015, itself with a margin of 45,700 to 61,700.",
      "A death can be a SUDEP death without the word on the certificate. A certifier may write seizure disorder or epilepsy, and that death then sits among the roughly " + e.ucd_year + " a year coded to epilepsy, where it cannot be told apart from other epilepsy deaths.",
      "A death certificate is the certifier's opinion from the information available at the time. These numbers cannot show how many SUDEP deaths went unnamed, or why any one certificate was worded as it was.",
      "The years differ. The people were counted for 2015 and the certificates are from " + e.named_period + ", the most recent five years and the period with the most certificates naming SUDEP.",
    ].forEach(t => limits.append(h("li", "", t)));
    into.append(limits);
  }

  function states(into) {
    bars(into, D.states.slice().sort((a, b) => b.r - a.r).map(r => ({
      label: r.g, value: r.r, text: r.r.toFixed(1), extra: r.ci.replace(" - ", " to "), tone: r.g === "Minnesota" ? "" : "off", sel: r.g === "Minnesota",
      tip: [[r.r.toFixed(1), "per 100,000, age-adjusted"], [r.ci.replace(" - ", " to "), "95% confidence interval"], [num(r.n), "deaths, 2018 to 2024"]],
    })), "Age-adjusted deaths per 100,000 residents a year, with the 95% confidence interval");
    note(into, "Minnesota's interval sits above those of Wisconsin, North Dakota and the United States. It touches Iowa's and overlaps South Dakota's, so those differences are not established.");
    note(into, "A state's rate depends partly on how often certifiers write epilepsy on a death certificate, which varies. A higher rate may mean more deaths, fuller recording, or both.");
  }

  const DRAW = { count, year, age, place, named, expected, states };
  function render() {
    tip.hide();
    const keep = fig.querySelector(".tip");
    fig.replaceChildren();
    fig.append(h("h1", "", "What Minnesota death certificates record"));
    fig.append(h("p", "lede", "Sudden Unexpected Death in Epilepsy has no code of its own on a death certificate, so Minnesota has no count of it. " +
      "These are the counts that do exist: the coded causes of death the CDC publishes, and a search of the written cause of death that the Minnesota Department of Health ran for EDAN."));
    seg(fig, "Look at", VIEWS.map(v => ({ id: v[0], label: v[1] })), view, (id) => { view = id; set({ show: view }); render(); });
    const body = h("div", "panel");
    fig.append(body);
    DRAW[view](body);
    const foot = h("div", "foot");
    [
      "Coded counts: " + CDC + ". CDC withholds any count from 1 to 9, shown here as fewer than 10.",
      "SUDEP by name: " + MDH + ". Shown as multi-year totals.",
      "Expected and named: " + RATES + ".",
      "The counts on this page come from death certificates. The one estimate, in the view Expected and named, is built from published rates and is not a Minnesota measurement. Nothing here describes any one person's risk.",
    ].forEach(t => foot.append(h("p", "", t)));
    fig.append(foot);
    if (keep) fig.append(keep);
  }
  render();
  // The view Expected and named drops the notes beside its bars on a narrow screen.
  let wide = fig.clientWidth >= 560;
  window.addEventListener("resize", () => { const now = fig.clientWidth >= 560; if (now !== wide) { wide = now; render(); } });
})();
