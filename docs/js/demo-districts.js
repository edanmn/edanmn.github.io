/* ==========================================================================
   demo-districts.js: one district's audit result beside districts like it.
   Data is window.DATA.d, one row per district, written by build_demos.py:
     [number, name, county, city, locale, enrollment, result, link to posted plan]
   result is posted | med | nothing | nocheck.

   "Similar" means the same locale (city, suburb, town or rural) with between
   half and twice the enrollment. If fewer than eight districts fit, every other
   district of that locale is used instead.
   ========================================================================== */
(function () {
  "use strict";
  const { h, num, pct, get, set, tips } = window.EDAN;
  const fig = document.getElementById("demo");
  const tip = tips(fig);
  const ALL = window.DATA.d.map(r => ({ isd: r[0], name: r[1], county: r[2], city: r[3], type: r[4], en: r[5], st: r[6], url: r[7] }));
  const WHEN = window.DATA.checked;

  const ORDER = ["posted", "med", "nothing", "nocheck"];
  const LABEL = { posted: "Seizure plan posted", med: "Medication policy only", nothing: "Nothing found", nocheck: "Could not check" };
  const KIND = { Rural: "rural", Town: "town", Suburb: "suburban", City: "city" };

  let me = ALL.find(d => d.isd === get("district")) || null;
  let showAll = false;

  const posted = (list) => list.filter(d => d.st === "posted").length;
  function peers(d) {
    const same = ALL.filter(x => x.type === d.type && x !== d);
    const near = d.en ? same.filter(x => x.en >= d.en / 2 && x.en <= d.en * 2) : [];
    return near.length >= 8 ? { list: near, sized: true } : { list: same, sized: false };
  }
  // CDC: about 0.6 percent of children have active epilepsy, between 1 in 170 and 1 in 150.
  const withEpilepsy = (students) => {
    const lo = Math.round(students / 170), hi = Math.round(students / 150);
    return lo === hi ? "about " + num(lo) : "about " + num(lo) + " to " + num(hi);
  };

  // Bring the top of the result into view. Inside a page, leave room for that page's fixed header.
  function toTop() {
    let frame = null;
    try { frame = window.frameElement; } catch (e) { frame = null; }
    if (!frame) return fig.scrollIntoView({ block: "start" });
    frame.style.scrollMarginTop = "5.5rem";
    frame.scrollIntoView({ block: "start" });
  }
  function pick(d) { me = d; showAll = false; set({ district: d ? d.isd : null }); render(); if (d) toTop(); }

  /* ---- Search: the same box as Find Your District ---- */
  function search(into) {
    const wrap = h("div", "ctl"), lab = h("label", "", "Type a school district, city or county");
    const q = h("input"), list = h("div", "list");
    q.type = "search"; q.id = "q"; q.autocomplete = "off"; q.placeholder = "e.g. Worthington, Roseau, Anoka";
    q.setAttribute("role", "combobox"); q.setAttribute("aria-autocomplete", "list"); q.setAttribute("aria-expanded", "false"); q.setAttribute("aria-controls", "matches");
    lab.htmlFor = "q"; list.id = "matches"; list.setAttribute("role", "listbox");
    if (me) q.value = me.name;
    let found = [], at = -1;
    const hay = (d) => (d.name + " " + d.county + " " + d.city + " " + d.isd).toLowerCase();
    function draw() {
      list.replaceChildren();
      found.forEach((d, i) => {
        const row = h("div", i === at ? "active" : "", d.name + " ");
        row.append(h("span", "", d.county + " County"));
        row.id = "m" + i; row.setAttribute("role", "option"); row.setAttribute("aria-selected", i === at ? "true" : "false");
        row.addEventListener("mousedown", (e) => { e.preventDefault(); pick(d); });
        list.append(row);
      });
      q.setAttribute("aria-expanded", found.length ? "true" : "false");
      if (at >= 0) { q.setAttribute("aria-activedescendant", "m" + at); list.children[at].scrollIntoView({ block: "nearest" }); }
      else q.removeAttribute("aria-activedescendant");
    }
    q.addEventListener("input", () => {
      const v = q.value.trim().toLowerCase();
      at = -1;
      if (v.length < 2) found = [];
      else {
        const hits = ALL.filter(d => hay(d).includes(v));
        const rank = (d) => d.name.toLowerCase().startsWith(v) ? 0 : (" " + d.name.toLowerCase()).includes(" " + v) ? 1 : 2;
        found = hits.sort((a, b) => rank(a) - rank(b) || a.name.localeCompare(b.name)).slice(0, 12);
      }
      draw();
    });
    q.addEventListener("keydown", (e) => {
      if (e.key === "Escape") { found = []; at = -1; draw(); return; }
      if (!found.length) return;
      if (e.key === "ArrowDown") { at = Math.min(at + 1, found.length - 1); e.preventDefault(); draw(); }
      else if (e.key === "ArrowUp") { at = Math.max(at - 1, 0); e.preventDefault(); draw(); }
      else if (e.key === "Enter") { e.preventDefault(); pick(found[at < 0 ? 0 : at]); }
    });
    q.addEventListener("blur", () => { found = []; at = -1; draw(); });
    wrap.append(lab, q, list);
    into.append(wrap);
  }

  /* ---- One bar split four ways, with the share that posts a plan beside it ---- */
  function stack(into, label, sub, list) {
    const lab = h("div", "lab", label), trk = h("div", "trk"), bar = h("div", "bar");
    if (sub) lab.append(h("small", "", sub));
    ORDER.forEach(k => {
      const n = list.filter(d => d.st === k).length;
      if (!n) return;
      const part = h("i", k);
      part.style.width = n / list.length * 100 + "%";
      tip.on(part, label, [[n + " of " + list.length, LABEL[k].toLowerCase()], [pct(n, list.length), "of this group"]]);
      bar.append(part);
    });
    const p = h("span", "pct", pct(posted(list), list.length) + " post a plan ");
    p.append(h("small", "", posted(list) + " of " + list.length));
    trk.append(bar, p);
    into.append(lab, trk);
  }

  function legend(into) {
    const key = h("ul", "legend");
    ORDER.forEach(k => { const li = h("li"); li.append(h("span", "chip " + k, LABEL[k])); key.append(li); });
    into.append(key);
  }

  function nameList(into, list, withLink) {
    const ul = h("ul", "names");
    list.forEach(d => {
      const li = h("li"), b = h("button", "", d.name);
      b.type = "button"; b.title = "Compare " + d.name;
      b.addEventListener("click", () => pick(d));
      li.append(b);
      if (withLink && d.url) {
        const a = h("a", "", "posted plan"), s = h("span");
        a.href = d.url; a.target = "_blank"; a.rel = "noopener";
        s.append((d.en ? num(d.en) + " students · " : ""), a);
        li.append(s);
      } else li.append(h("span", "chip " + d.st, LABEL[d.st]));
      ul.append(li);
    });
    into.append(ul);
  }

  function statewide(into) {
    into.append(h("h2", "", "By kind of district"));
    const g = h("div", "stack");
    [["City", "City districts"], ["Suburb", "Suburban districts"], ["Town", "Town districts"], ["Rural", "Rural districts"]].forEach(([t, label]) =>
      stack(g, label, "", ALL.filter(d => d.type === t)));
    stack(g, "All Minnesota districts", "", ALL);
    into.append(g);
    legend(into);
  }

  function district(into) {
    const d = me, grp = peers(d), kind = KIND[d.type];
    const county = ALL.filter(x => x.county === d.county && x !== d);
    const group = grp.sized
      ? "other " + kind + " districts of similar size"
      : "other " + kind + " districts";
    const without = grp.list.filter(x => x.st !== "posted"), kids = without.reduce((a, x) => a + x.en, 0);
    into.append(h("h2", "", d.name + ", " + d.county + " County"));
    const big = h("div", "big");
    const fact = (value, label, cls) => { const b = h("div", cls || ""); b.append(h("b", "", value), h("span", "", label)); big.append(b); };
    fact(LABEL[d.st], "what we found on the district's website");
    if (d.en) {
      fact(num(d.en), "students enrolled");
      fact(withEpilepsy(d.en), "students with epilepsy, estimated");
    }
    into.append(big);
    if (d.en) into.append(h("p", "small", "The estimate applies the CDC's national rate for children, about 1 in 150 to 1 in 170, to the district's enrollment. It is not a count of students in this district."));

    into.append(h("h2", "", "How it compares"));
    const g = h("div", "stack");
    stack(g, grp.sized ? "Similar districts" : "Other " + kind + " districts", grp.sized ? kind + ", " + num(Math.round(d.en / 2)) + " to " + num(d.en * 2) + " students" : "", grp.list);
    if (county.length) stack(g, "Rest of " + d.county + " County", "", county);
    if (grp.sized) stack(g, "All " + kind + " districts", "", ALL.filter(x => x.type === d.type));
    stack(g, "All Minnesota districts", "", ALL);
    into.append(g);
    legend(into);

    into.append(h("h2", "", grp.sized ? "The " + grp.list.length + " similar districts, smallest to largest" : "The " + grp.list.length + " other " + kind + " districts, smallest to largest"));
    into.append(h("p", "small", "Each square is one district, and the outlined one is " + d.name + ". Pick a square to compare that district instead." +
      (kids ? " The " + without.length + " without a posted plan enroll " + num(kids) + " students, " + withEpilepsy(kids) + " of whom are estimated to have epilepsy." : "")));
    const grid = h("div", "grid");
    grp.list.concat([d]).sort((a, b) => a.en - b.en).forEach(x => {
      const sq = h("button", "sq " + x.st + (x === d ? " me" : ""));
      sq.type = "button"; sq.setAttribute("aria-label", x.name + (x.en ? ", " + num(x.en) + " students: " : ": ") + LABEL[x.st]);
      tip.on(sq, x.name, [x.en ? [num(x.en), "students"] : ["", "enrollment not listed"], [LABEL[x.st], x.county + " County"]]);
      if (x !== d) sq.addEventListener("click", () => pick(x));
      grid.append(sq);
    });
    into.append(grid);

    const examples = grp.list.filter(x => x.st === "posted").sort((a, b) => Math.abs(a.en - d.en) - Math.abs(b.en - d.en));
    if (examples.length) {
      into.append(h("h2", "", grp.sized ? "Similar districts that post a seizure plan" : "Other " + kind + " districts that post a seizure plan"));
      into.append(h("p", "small", "Closest in enrollment first. Each link opens the page or document we found in " + WHEN + "; districts move their pages, so some links may have changed."));
      nameList(into, showAll ? examples : examples.slice(0, 12), true);
      if (examples.length > 12 && !showAll) {
        const act = h("div", "act"), b = h("button", "", "Show all " + examples.length);
        b.type = "button"; b.addEventListener("click", () => { showAll = true; render(); });
        act.append(b); into.append(act);
      }
    }
    if (county.length) {
      into.append(h("h2", "", "The rest of " + d.county + " County"));
      nameList(into, county.slice().sort((a, b) => a.name.localeCompare(b.name)), false);
    }
    const act = h("div", "act"), back = h("button", "", "Back to the statewide view");
    back.type = "button"; back.addEventListener("click", () => pick(null));
    act.append(back); into.append(act);
  }

  function render() {
    tip.hide();
    const keep = fig.querySelector(".tip");
    fig.replaceChildren();
    fig.append(h("h1", "", "How does your district compare?"));
    fig.append(h("p", "lede", "In " + WHEN + " we checked the website of every Minnesota school district for a posted seizure plan. Pick a district to see its result beside districts of the same kind and size, the rest of its county and the state."));
    search(fig);
    const body = h("div", "panel");
    fig.append(body);
    if (me) district(body); else statewide(body);
    const foot = h("div", "foot");
    [
      "Source: EDAN audit of the public websites of all " + ALL.length + " Minnesota school districts, " + WHEN + ".",
      "This records whether a seizure plan was posted publicly online in " + WHEN + ". A district with nothing posted may keep plans on file or on pages we could not reach, so this is not a measure of legal compliance or of how safe a school is.",
      "Similar districts share the same locale (city, suburb, town or rural) and have between half and twice the enrollment. Where fewer than eight districts fit, every other district of that locale is used.",
    ].forEach(t => foot.append(h("p", "", t)));
    fig.append(foot);
    if (keep) fig.append(keep);
  }
  render();
})();
