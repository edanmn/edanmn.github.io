/* ==========================================================================
   charts.js — draws the chart a page describes in SPEC into <figure id="chart">.
   Styling is in docs/css/charts.css; the pages are written by edan_charts.py.

   There is no chart library. Bars and columns are plain HTML, lines, bubbles and
   the county map are SVG, so a chart is on screen as soon as its page is, and it
   answers a pointer straight away.

   SPEC.type is one of:
     "bars"     rows: [{label, value, text, tone?, tip?}]        scale?: "log"
     "columns"  cols: [{label, value, text, sub?, tip?}]         ymax?, yTitle?
     "lines"    x: [..], series: [{name, values, on?}]           yTitle?, toggle?
     "bubbles"  pts: [{name, x, y, n}]                           xTitle, yTitle, ymax
     "counties" areas: [{name, d, v, n}], h, bins                legend, valueLabel
   Every chart also takes title, and may take sub, axis, note, head (table headings).
   tip is a list of [value, label] pairs for the hover card.
   ========================================================================== */
(function () {
  "use strict";
  const S = window.SPEC, fig = document.getElementById("chart");
  const NS = "http://www.w3.org/2000/svg";
  function h(name, cls, text) {
    const e = document.createElement(name);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  function s(name, attrs, parent) {
    const e = document.createElementNS(NS, name);
    for (const a in attrs) e.setAttribute(a, attrs[a]);
    if (parent) parent.appendChild(e);
    return e;
  }
  const num = (v) => typeof v === "number" ? v.toLocaleString("en-US") : v;
  const short = (v) => v >= 10000 ? v / 1000 + "k" : num(v);                  // axis ticks: 50,000 reads as 50k
  // A round step for an axis, so ticks land on numbers people expect.
  function step(span) {
    const p = Math.pow(10, Math.floor(Math.log10(span))), m = span / p;
    return (m <= 1 ? 1 : m <= 2 ? 2 : m <= 2.5 ? 2.5 : m <= 5 ? 5 : 10) * p;
  }
  function scale(max, fixed) {                                                 // {top, ticks} for an axis from 0
    if (fixed === 100) return { top: 100, ticks: [0, 25, 50, 75, 100] };
    const st = step(max / 4), top = fixed || Math.ceil(max / st) * st, ticks = [];
    for (let t = 0; t <= top + 1e-9; t += st) ticks.push(+t.toPrecision(12));
    return { top, ticks };
  }

  fig.append(h("h1", "", S.title));
  if (S.sub) fig.append(h("p", "sub", S.sub));
  const body = h("div");
  fig.append(body);

  /* ---- Hover card ---------------------------------------------------------
     One card, filled with text nodes, placed beside the pointer and growing
     from the pointer's side. Values lead; what they measure follows. */
  const tip = h("div", "tip");
  tip.setAttribute("role", "status");
  fig.append(tip);
  const at = (e) => { const b = fig.getBoundingClientRect(); return [e.clientX - b.left, e.clientY - b.top]; };
  function showTip(title, rows, x, y) {
    tip.replaceChildren(h("b", "", title));
    const dl = h("dl");
    rows.forEach(([value, label, colour]) => {
      const dt = h("dt");
      if (colour) { const key = h("span", "sw"); key.style.background = colour; dt.append(key); }
      dt.append(String(value));
      dl.append(dt, h("dd", "", label));
    });
    if (rows.length) tip.append(dl);
    tip.classList.add("on");
    const W = fig.clientWidth, H = fig.clientHeight, tw = tip.offsetWidth, th = tip.offsetHeight;
    let left = x + 14, top = y + 14;
    if (left + tw > W) left = x - 14 - tw;
    if (left < 0) left = Math.max(0, (W - tw) / 2);
    if (top + th > H) top = Math.max(0, y - 14 - th);
    tip.style.left = left + "px"; tip.style.top = top + "px";
    tip.style.transformOrigin = (left < x ? "right " : "left ") + (top < y ? "bottom" : "top");
  }
  const hideTip = () => tip.classList.remove("on");
  function hover(el, title, rows) {                    // a whole bar, row or column answers, not just its ink
    const show = (e) => showTip(title, rows, ...at(e));
    el.addEventListener("pointermove", show);
    el.addEventListener("pointerdown", show);
    el.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") hideTip(); });
  }
  document.addEventListener("pointerdown", (e) => { if (!e.target.closest || !e.target.closest(".row,.col,svg")) hideTip(); });

  /* ---- Bars ---------------------------------------------------------------- */
  function bars(rows, into) {
    const values = rows.map(r => r.value), max = Math.max(...values);
    const floor = S.scale === "log" ? Math.pow(10, Math.floor(Math.log10(Math.min(...values)))) : 0;
    const share = (v) => S.scale === "log" ? Math.log10(v / floor) / Math.log10(max / floor) : v / max;
    // Every bar leaves the same room for its value, so lengths can be compared with each other.
    const room = (Math.max(...rows.map(r => String(r.text).length)) + 1) * 0.56;
    const wrap = h("div", "bars" + (rows.length > 12 ? " dense" : ""));
    rows.forEach(r => {
      const row = h("div", "row"), track = h("div", "track"), bar = h("div", "bar" + (r.tone ? " " + r.tone : ""));
      bar.style.width = "calc((100% - " + room.toFixed(2) + "em) * " + Math.max(0, share(r.value)).toFixed(4) + ")";
      track.append(bar, h("span", "val", r.text));
      row.append(h("div", "lab", r.label), track);
      hover(row, r.label, r.tip || [[r.text, S.axis || ""]]);
      wrap.append(row);
    });
    into.append(wrap);
    if (S.axis) into.append(h("p", "axis", S.axis));
  }

  /* ---- Columns --------------------------------------------------------------
     On a screen too narrow to stand the columns side by side, the same numbers
     are drawn as bars instead. */
  function columns(into) {
    if (S.cols.length * 50 > into.clientWidth) {
      return bars(S.cols.map(c => ({ label: c.label, value: c.value, text: c.sub ? c.text + " (" + c.sub + ")" : c.text, tip: c.tip })), into);
    }
    const ax = scale(Math.max(...S.cols.map(c => c.value)), S.ymax);
    const wrap = h("div", "cols"), ticks = h("div", "ticks"), plot = h("div", "plot"), labs = h("div", "labs");
    if (S.yTitle) wrap.append(h("div", "ytitle", S.yTitle));
    ax.ticks.forEach(t => {
      const lab = h("span", "", short(t));
      lab.style.bottom = t / ax.top * 100 + "%";
      ticks.append(lab);
      if (t) { const line = h("i"); line.style.bottom = t / ax.top * 100 + "%"; plot.append(line); }
    });
    S.cols.forEach(c => {
      const col = h("div", "col"), bar = h("div", "bar"), cap = h("div", "cap", c.text), p = c.value / ax.top * 100 + "%";
      bar.style.height = p; cap.style.bottom = p;
      if (c.sub) cap.append(h("small", "", c.sub));
      col.append(bar, cap);
      hover(col, c.label, c.tip || [[c.text, S.yTitle || ""]]);
      plot.append(col);
      labs.append(h("span", "", c.label));
    });
    wrap.append(ticks, plot, labs);
    into.append(wrap);
    if (S.axis) into.append(h("p", "axis", S.axis));
  }

  /* ---- Lines ----------------------------------------------------------------- */
  const colour = (i) => i < 6 ? "var(--c" + (i + 1) + ")" : "var(--off)";      // the seventh line on is grey: there are only so many colours people can tell apart
  let shown = S.series ? S.series.map(d => d.on !== false) : [];
  function lines(into) {
    const key = h("ul", "key");
    S.series.forEach((d, i) => {
      const li = h("li"), sw = h("span", "sw");
      sw.style.background = colour(i);
      if (S.toggle) {
        const b = h("button");
        b.type = "button"; b.setAttribute("aria-pressed", shown[i]);
        b.append(sw, d.name);
        b.addEventListener("click", () => { shown[i] = !shown[i]; render(); });
        li.append(b);
      } else li.append(sw, d.name);
      key.append(li);
    });
    into.append(key);
    if (S.yTitle) into.append(h("p", "sub", S.yTitle));

    const live = S.series.map((d, i) => i).filter(i => shown[i]);
    const W = into.clientWidth, H = W < 480 ? 230 : 280, n = S.x.length;
    const endLabels = live.length <= 4 && W >= 520;
    const m = { l: 40, r: endLabels ? Math.min(210, Math.max(...live.map(i => S.series[i].name.length), 4) * 6.4 + 16) : 14, t: 10, b: 24 };
    const ax = scale(Math.max(1, ...live.flatMap(i => S.series[i].values.filter(v => v != null))));
    const X = (i) => m.l + i * (W - m.l - m.r) / (n - 1), Y = (v) => m.t + (1 - v / ax.top) * (H - m.t - m.b);
    const svg = s("svg", { viewBox: "0 0 " + W + " " + H, height: H, role: "img", "aria-label": S.title + ". The table below has every number." });
    ax.ticks.forEach(t => {
      s("line", { class: t ? "gridline" : "baseline", x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) }, svg);
      s("text", { x: m.l - 6, y: Y(t) + 4, "text-anchor": "end" }, svg).textContent = short(t);
    });
    S.x.forEach((x, i) => { s("text", { x: X(i), y: H - 6, "text-anchor": "middle" }, svg).textContent = x; });
    const cross = s("line", { class: "cross", y1: m.t, y2: H - m.b }, svg);
    const ends = [];
    live.forEach(i => {
      const pts = S.series[i].values.map((v, j) => v == null ? null : [X(j), Y(v)]);
      // A gap in the data is a gap in the line.
      const d = pts.reduce((a, p, j) => a + (p ? (j && pts[j - 1] ? "L" : "M") + p[0].toFixed(1) + "," + p[1].toFixed(1) : ""), "");
      s("path", { class: "series", d: d, style: "stroke:" + colour(i) }, svg);
      const last = pts.filter(Boolean).pop();
      if (last) { s("circle", { class: "dot", cx: last[0], cy: last[1], r: 4, style: "fill:" + colour(i) }, svg); ends.push([last, S.series[i].name]); }
    });
    // Name the lines at their ends only when the names would not sit on top of each other.
    ends.sort((a, b) => a[0][1] - b[0][1]);
    if (endLabels && ends.every((e, i) => !i || e[0][1] - ends[i - 1][0][1] > 13)) {
      ends.forEach(([p, name]) => { s("text", { class: "endlab", x: p[0] + 9, y: p[1] + 4 }, svg).textContent = name; });
    }
    const marks = live.map(i => s("circle", { class: "dot", r: 4, style: "display:none;fill:" + colour(i) }, svg));
    // The pointer picks a year, not a line: the card lists every line shown, largest first.
    function point(e) {
      const box = svg.getBoundingClientRect(), j = Math.max(0, Math.min(n - 1, Math.round((e.clientX - box.left - m.l) / ((W - m.l - m.r) / (n - 1)))));
      cross.setAttribute("x1", X(j)); cross.setAttribute("x2", X(j)); cross.style.display = "block";
      const rows = [];
      live.forEach((i, k) => {
        const v = S.series[i].values[j];
        marks[k].style.display = v == null ? "none" : "block";
        if (v != null) { marks[k].setAttribute("cx", X(j)); marks[k].setAttribute("cy", Y(v)); rows.push([v, S.series[i].name, colour(i)]); }
      });
      rows.sort((a, b) => b[0] - a[0]);
      showTip(String(S.x[j]), rows.map(r => [num(r[0]), r[1], r[2]]), ...at(e));
    }
    svg.addEventListener("pointermove", point);
    svg.addEventListener("pointerdown", point);
    svg.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") { hideTip(); cross.style.display = "none"; marks.forEach(c => c.style.display = "none"); } });
    into.append(svg);
  }

  /* ---- Bubbles ---------------------------------------------------------------- */
  function bubbles(into) {
    if (S.yTitle) into.append(h("p", "sub", S.yTitle));
    const W = into.clientWidth, H = W < 480 ? 280 : 330, m = { l: 36, r: 14, t: 12, b: 42 };
    const xs = S.pts.map(p => p.x), st = step((Math.max(...xs) - Math.min(...xs)) / 4);
    const x0 = Math.floor(Math.min(...xs) / st) * st, x1 = Math.ceil(Math.max(...xs) / st) * st, ay = scale(0, S.ymax || 100);
    const X = (v) => m.l + (v - x0) / (x1 - x0) * (W - m.l - m.r), Y = (v) => m.t + (1 - v / ay.top) * (H - m.t - m.b);
    const R = (p) => 3 + Math.sqrt(p.n) * 2.4;
    const svg = s("svg", { viewBox: "0 0 " + W + " " + H, height: H, role: "img", "aria-label": S.title + ". The table below has every number." });
    ay.ticks.forEach(t => {
      s("line", { class: t ? "gridline" : "baseline", x1: m.l, x2: W - m.r, y1: Y(t), y2: Y(t) }, svg);
      s("text", { x: m.l - 6, y: Y(t) + 4, "text-anchor": "end" }, svg).textContent = t;
    });
    for (let t = x0; t <= x1 + 1e-9; t += st) s("text", { x: X(t), y: H - m.b + 16, "text-anchor": "middle" }, svg).textContent = +t.toPrecision(6);
    s("text", { class: "axt", x: (m.l + W - m.r) / 2, y: H - 6, "text-anchor": "middle" }, svg).textContent = S.xTitle;
    // Largest first, so a small county is never hidden under a big one.
    S.pts.slice().sort((a, b) => b.n - a.n).forEach(p => s("circle", { class: "bubble", cx: X(p.x), cy: Y(p.y), r: R(p) }, svg));
    const ring = s("circle", { class: "ring" }, svg);
    // The pointer only has to be near a bubble, not on it.
    function point(e) {
      const box = svg.getBoundingClientRect(), mx = e.clientX - box.left, my = e.clientY - box.top;
      let best = null, bd = 26 * 26;
      S.pts.forEach(p => { const dx = X(p.x) - mx, dy = Y(p.y) - my, d = dx * dx + dy * dy; if (d < bd) { bd = d; best = p; } });
      if (!best) { hideTip(); ring.style.display = "none"; return; }
      ring.setAttribute("cx", X(best.x)); ring.setAttribute("cy", Y(best.y)); ring.setAttribute("r", R(best) + 2); ring.style.display = "block";
      showTip(best.name, [[best.x + "%", S.tip[0]], [best.y + "%", S.tip[1]], [best.n, S.tip[2]]], ...at(e));
    }
    svg.addEventListener("pointermove", point);
    svg.addEventListener("pointerdown", point);
    svg.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") { hideTip(); ring.style.display = "none"; } });
    into.append(svg);
  }

  /* ---- County map --------------------------------------------------------------- */
  function counties(into) {
    const cls = (v) => S.bins.reduce((k, b) => k + (v > b), 0);
    const wrap = h("div", "mapfig"), key = h("div");
    const svg = s("svg", { viewBox: "0 0 1000 " + S.h, role: "img", "aria-label": S.title + ". The table below has every county." }, wrap);
    S.areas.forEach(a => {
      const path = s("path", { class: "area k" + cls(a.v), d: a.d }, svg);
      const show = (e) => { edge.setAttribute("d", a.d); edge.style.display = "block"; showTip(a.name, [[a.v + "%", S.valueLabel], [a.n, a.n === 1 ? "district" : "districts"]], ...at(e)); };
      path.addEventListener("pointermove", show);
      path.addEventListener("pointerdown", show);
    });
    const edge = s("path", { class: "areahit" }, svg);
    svg.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") { hideTip(); edge.style.display = "none"; } });
    const labels = S.bins.map((b, i) => i ? S.bins[i - 1] + " to " + b + "%" : b + "% or less").concat("More than " + S.bins[S.bins.length - 1] + "%");
    const list = h("ul", "key");
    labels.forEach((label, i) => {
      const li = h("li");
      li.append(h("span", "sw box k" + i), label, h("span", "n", String(S.areas.filter(a => cls(a.v) === i).length)));
      list.append(li);
    });
    key.append(h("h2", "", S.legend), list);
    if (S.note) key.append(h("p", "note", S.note));
    wrap.append(key);
    into.append(wrap);
  }

  /* ---- Table view: every number on the chart, without hovering ------------------ */
  function tableRows() {
    if (S.type === "bars") return S.rows.map(r => [r.label, r.text].concat((r.tip || []).slice(1).map(t => t[0])));
    if (S.type === "columns") return S.cols.map(c => [c.label].concat(c.sub ? [c.sub] : [], [c.text], (c.tip || []).slice(1).map(t => t[0])));
    if (S.type === "lines") return S.x.map((x, j) => [String(x)].concat(S.series.map(d => d.values[j] == null ? "" : num(d.values[j]))));
    if (S.type === "bubbles") return S.pts.slice().sort((a, b) => b.y - a.y || a.name.localeCompare(b.name)).map(p => [p.name, p.x + "%", p.y + "%", p.n]);
    return S.areas.slice().sort((a, b) => b.v - a.v || a.name.localeCompare(b.name)).map(a => [a.name, a.v + "%", a.n]);
  }
  function addTable() {
    const head = S.type === "lines" ? [S.head[0]].concat(S.series.map(d => d.name)) : S.head;
    if (!head) return;                                 // a chart whose every value is already written on it needs no table
    const tools = h("div", "tools"), button = h("button", "", "Show as a table"), wrap = h("div", "tablewrap");
    button.type = "button"; button.setAttribute("aria-expanded", "false");
    wrap.tabIndex = 0;
    button.addEventListener("click", () => {
      const open = wrap.style.display !== "block";
      if (open && !wrap.firstChild) {
        const t = h("table"), tr = t.createTHead().insertRow(), tb = t.createTBody();
        head.forEach((label, i) => { const th = h("th", i ? "r" : "", label); th.scope = "col"; tr.append(th); });
        tableRows().forEach(cells => { const row = tb.insertRow(); cells.forEach((c, i) => row.append(h("td", i ? "r" : "", c))); });
        wrap.append(t);
      }
      wrap.style.display = open ? "block" : "none";
      button.textContent = open ? "Hide the table" : "Show as a table";
      button.setAttribute("aria-expanded", open);
    });
    tools.append(button);
    fig.append(tools, wrap);
  }

  /* ---- Draw, and draw again when the width changes ------------------------------- */
  let width = 0;
  function render() {
    body.replaceChildren();
    hideTip();
    if (S.type === "bars") bars(S.rows, body);
    else if (S.type === "columns") columns(body);
    else if (S.type === "lines") lines(body);
    else if (S.type === "bubbles") bubbles(body);
    else counties(body);
    if (S.note && S.type !== "counties") body.append(h("p", "note", S.note));
  }
  function fit() { const w = body.clientWidth; if (w && w !== width) { width = w; render(); } }
  fit();
  addTable();
  if ("ResizeObserver" in window) new ResizeObserver(fit).observe(fig); else window.addEventListener("resize", fit);
})();
