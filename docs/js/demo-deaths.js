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
   ========================================================================== */
(function () {
  "use strict";
  const { h, num, pct, get, set, say, seg, tips } = window.EDAN;
  const D = window.DATA, fig = document.getElementById("demo");
  const tip = tips(fig);

  const CDC = "CDC WONDER, Multiple Cause of Death, Minnesota residents, 2018 to 2024";
  const MDH = "Minnesota Department of Health, Minnesota Center for Health Statistics, death certificate data, custom tabulation for EDAN, October 2026";
  const DEF = {
    any: { label: "Epilepsy or seizures mentioned", sub: "G40, G41 or R56", said: "mentioned epilepsy or seizures",
      long: "Any of the codes G40 (epilepsy), G41 (status epilepticus) or R56 (convulsions) anywhere on the certificate. R56 takes in seizures recorded without an epilepsy diagnosis, so this is the widest count." },
    epi: { label: "Epilepsy mentioned", sub: "G40 or G41", said: "mentioned epilepsy",
      long: "G40 or G41 anywhere on the certificate, whether as the underlying cause or as a contributing one." },
    ucd: { label: "Epilepsy as the underlying cause", sub: "G40 or G41", said: "gave epilepsy as the underlying cause",
      long: "G40 or G41 chosen as the single underlying cause of death, the condition that started the chain of events." },
  };
  const VIEWS = [["count", "The count"], ["year", "By year"], ["age", "By age"], ["place", "Where people died"], ["named", "SUDEP by name"], ["states", "Other states"]];
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
    say(into, "From 2018 to 2024, " + num(t.any) + " Minnesota death certificates mentioned epilepsy or seizures, " + num(t.epi) +
      " mentioned epilepsy, and " + num(t.ucd) + " gave epilepsy as the underlying cause. In the same seven years, " + s.same_years +
      " certificates named SUDEP in the cause-of-death text.", CDC + "; " + MDH);
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
    const rows = D.year[def], first = rows[0], last = rows[rows.length - 1];
    say(into, "Minnesota death certificates that " + DEF[def].said + " numbered " + num(first.n) + " in " + first.g + " and " + num(last.n) + " in " + last.g +
      ", and " + num(D.total[def]) + " across the seven years.", CDC);
    columns(into, rows.map(r => ({ label: r.g, value: r.n, text: num(r.n),
      tip: [[num(r.n), "deaths"], [r.r, "per 100,000 residents"], [r.ci, "95% confidence interval"]] })), "Deaths a year");
  }

  function age(into) {
    defPicker(into);
    seg(into, "Show", [{ id: "deaths", label: "Number of deaths" }, { id: "rate", label: "Deaths per 100,000 residents" }], measure,
      (id) => { measure = id; set({ as: measure === "rate" ? "rate" : null }); render(); });
    const rows = D.age[def], known = rows.filter(r => r.n != null);
    const most = known.reduce((a, b) => b.n > a.n ? b : a), steepest = known.reduce((a, b) => b.r > a.r ? b : a);
    const young = rows.filter(r => /^(< 1|1-4|5-14|15-24|25-34|35-44)/.test(r.g));
    let text = "Among Minnesota deaths from 2018 to 2024 that " + DEF[def].said + ", the largest number was at ages " + ageName(most.g).toLowerCase() +
      " (" + num(most.n) + "), and the rate was highest at ages " + ageName(steepest.g).toLowerCase() + " (" + steepest.r + " per 100,000 residents a year).";
    if (young.every(r => r.n != null)) {
      const n = young.reduce((a, r) => a + r.n, 0);
      text += " People under 45 were " + num(n) + " of the " + num(D.total[def]) + " (" + pct(n, D.total[def]) + ").";
    }
    say(into, text, CDC);
    bars(into, rows.map(r => {
      const v = measure === "rate" ? r.r : r.n;
      return { label: ageName(r.g), value: v, text: v == null ? "fewer than 10 deaths" : measure === "rate" ? String(v) : num(v),
        extra: measure === "rate" && r.ci ? r.ci.replace(" - ", " to ") : "",
        tip: r.n == null ? [["1 to 9", "deaths, withheld by CDC"]] : [[num(r.n), "deaths, 2018 to 2024"], [r.r, "per 100,000 residents a year"], [r.ci.replace(" - ", " to "), "95% confidence interval"]] };
    }), measure === "rate" ? "Deaths per 100,000 residents a year, with the 95% confidence interval" : "Deaths, 2018 to 2024");
  }

  function place(into) {
    seg(into, "Whose deaths", Object.keys(SCOPE).map(k => ({ id: k, label: SCOPE[k].label, sub: SCOPE[k].sub })), scope, (id) => { scope = id; set({ who: scope }); render(); });
    const p = D.place[scope], home = p.rows.find(r => r.g === "Decedent's home");
    say(into, "Of " + num(p.total) + " " + SCOPE[scope].who + " from 2018 to 2024, " + num(home.n) + " (" + pct(home.n, p.total) + ") died at home.", CDC);
    bars(into, p.rows.slice().sort((a, b) => (b.n || 0) - (a.n || 0)).map(r => ({
      label: PLACE[r.g] || r.g, value: r.n, text: r.n == null ? "fewer than 10" : num(r.n), extra: r.n == null ? "" : pct(r.n, p.total),
      tone: r.g === "Decedent's home" ? "" : "off", sel: r.g === "Decedent's home",
      tip: r.n == null ? [["1 to 9", "deaths, withheld by CDC"]] : [[num(r.n), "of " + num(p.total) + " deaths"], [pct(r.n, p.total), "of this group"]],
    })), "Deaths, 2018 to 2024");
    note(into, "The coded files do not record whether anyone was present or whether the person was asleep. Place of death is the closest public measure. Dying at home is not proof of SUDEP, and some SUDEP deaths happen elsewhere.");
  }

  function named(into) {
    const s = D.sudep, p = s.periods;
    say(into, "From 2011 to 2024, " + s.total + " Minnesota death certificates named SUDEP in the cause-of-death text: " + p[0][1] + " in " + p[0][0] + ", " +
      p[1][1] + " in " + p[1][0] + " and " + p[2][1] + " in " + p[2][0] + ". Of the " + s.total + " people, " + s.under45 + " were under 45.", MDH);
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

  function states(into) {
    const mn = D.states.find(r => r.g === "Minnesota"), us = D.states.find(r => r.g === "United States");
    say(into, "Counting every death certificate that mentions epilepsy, Minnesota's age-adjusted death rate for 2018 to 2024 was " + mn.r.toFixed(1) + " per 100,000 residents a year, against " +
      us.r.toFixed(1) + " for the United States.", "CDC WONDER, Multiple Cause of Death, 2018 to 2024");
    bars(into, D.states.slice().sort((a, b) => b.r - a.r).map(r => ({
      label: r.g, value: r.r, text: r.r.toFixed(1), extra: r.ci.replace(" - ", " to "), tone: r.g === "Minnesota" ? "" : "off", sel: r.g === "Minnesota",
      tip: [[r.r.toFixed(1), "per 100,000, age-adjusted"], [r.ci.replace(" - ", " to "), "95% confidence interval"], [num(r.n), "deaths, 2018 to 2024"]],
    })), "Age-adjusted deaths per 100,000 residents a year, with the 95% confidence interval");
    note(into, "Minnesota's interval sits above those of Wisconsin, North Dakota and the United States. It touches Iowa's and overlaps South Dakota's, so those differences are not established.");
    note(into, "A state's rate depends partly on how often certifiers write epilepsy on a death certificate, which varies. A higher rate may mean more deaths, fuller recording, or both.");
  }

  const DRAW = { count, year, age, place, named, states };
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
      "This page publishes counts. It does not estimate how many SUDEP deaths occur, and it says nothing about any one person's risk.",
    ].forEach(t => foot.append(h("p", "", t)));
    fig.append(foot);
    if (keep) fig.append(keep);
  }
  render();
})();
