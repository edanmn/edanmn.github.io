/* ==========================================================================
   demos.js: helpers shared by the three interactive pages in docs/sims/.
   Each page keeps what the reader picked in its own address, so a view can be
   linked to.
   ========================================================================== */
window.EDAN = (function () {
  "use strict";

  function h(name, cls, text) {
    const e = document.createElement(name);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }
  const num = (v) => Number(v).toLocaleString("en-US");
  const usd = (v) => "$" + Number(v).toLocaleString("en-US", { minimumFractionDigits: v % 1 ? 2 : 0, maximumFractionDigits: 2 });
  const pct = (a, b) => b ? Math.round(a / b * 100) + "%" : "n/a";

  /* ---- What the reader picked, kept in the address ---- */
  const params = new URLSearchParams(location.search);
  const get = (k, fallback) => params.has(k) ? params.get(k) : fallback;
  function set(values) {
    for (const k in values) {
      if (values[k] == null || values[k] === "") params.delete(k); else params.set(k, values[k]);
    }
    const q = params.toString();
    try { history.replaceState(null, "", location.pathname + (q ? "?" + q : "")); } catch (e) { /* opened from a file */ }
  }
  // A row of buttons where one is chosen.
  function seg(into, label, options, current, onPick) {
    const wrap = h("div", "ctl"), row = h("div", "seg");
    row.setAttribute("role", "group"); row.setAttribute("aria-label", label);
    wrap.append(h("span", "", label), row);
    options.forEach(o => {
      const b = h("button", "", o.label);
      b.type = "button";
      if (o.sub) b.append(h("small", "", o.sub));
      b.setAttribute("aria-pressed", o.id === current ? "true" : "false");
      if (o.off) b.disabled = true;
      b.addEventListener("click", () => onPick(o.id));
      row.append(b);
    });
    into.append(wrap);
    return wrap;
  }

  /* ---- Hover card, the same one the charts use ---- */
  function tips(fig) {
    const tip = h("div", "tip");
    tip.setAttribute("role", "status");
    fig.append(tip);
    function show(title, rows, e) {
      tip.replaceChildren(h("b", "", title));
      const dl = h("dl");
      rows.forEach(([value, label]) => dl.append(h("dt", "", String(value)), h("dd", "", label)));
      if (rows.length) tip.append(dl);
      tip.classList.add("on");
      const b = fig.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
      const W = fig.clientWidth, H = fig.clientHeight, tw = tip.offsetWidth, th = tip.offsetHeight;
      let left = x + 14, top = y + 14;
      if (left + tw > W) left = x - 14 - tw;
      if (left < 0) left = Math.max(0, (W - tw) / 2);
      if (top + th > H) top = Math.max(0, y - 14 - th);
      tip.style.left = left + "px"; tip.style.top = top + "px";
      tip.style.transformOrigin = (left < x ? "right " : "left ") + (top < y ? "bottom" : "top");
    }
    const hide = () => tip.classList.remove("on");
    function on(el, title, rows) {
      el.dataset.tip = "1";
      const go = (e) => show(title, typeof rows === "function" ? rows() : rows, e);
      el.addEventListener("pointermove", go);
      el.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") hide(); });
      el.addEventListener("blur", hide);
    }
    document.addEventListener("pointerdown", (e) => { if (!e.target.closest || !e.target.closest("[data-tip]")) hide(); });
    return { on, hide };
  }

  return { h, num, usd, pct, get, set, seg, tips };
})();
