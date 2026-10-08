/* ==========================================================================
   reactbits.js — modern/interactive layer for the EDAN textbook.
   Effects modelled on reactbits.dev (Aurora, Spotlight Card), rebuilt in
   vanilla JS so they run in a static MkDocs Material build, plus the home
   page search, the light/dark fade and the swipeable phone menu.

   Principles:
   - Content is fully usable without JS; this only adds polish.
   - Content never waits on an animation, and figures are shown as written.
   - Respect prefers-reduced-motion.
   - Re-run on every page via Material's document$ (navigation.instant).
   ========================================================================== */
(function () {
  "use strict";

  var prefersReduced = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  function isHomePage() {
    var p = location.pathname.replace(/index\.html$/, "").replace(/\/+$/, "");
    return p === "";
  }

  /* ---- Spotlight Card / hover lift -------------------------------------- */
  function initSpotlight() {
    // Only collapsible blocks: they are the ones a press does something to.
    var cards = document.querySelectorAll(".md-content .md-typeset details");
    cards.forEach(function (card) {
      card.classList.add("rb-spot");
      if (prefersReduced) return;
      card.addEventListener("pointermove", function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty("--rb-x", e.clientX - r.left + "px");
        card.style.setProperty("--rb-y", e.clientY - r.top + "px");
      });
    });
  }

  /* ---- Aurora background (home only) -------------------------------------- */
  function initHome() {
    var existing = document.querySelector(".rb-aurora");
    if (existing) existing.remove();
    if (!isHomePage()) return;

    var aurora = document.createElement("div");
    aurora.className = "rb-aurora";
    aurora.setAttribute("aria-hidden", "true");
    document.body.appendChild(aurora);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        aurora.classList.add("rb-in");
      });
    });

  }

  // Home page search box: the same dropdown as the Find Your District lookup. Matching and
  // ranking follow docs/find-your-district/district_lookup.html; picking a district opens it.
  var findNames = null;
  function initFind() {
    var q = document.getElementById("edan-find-q");
    if (!q || q.getAttribute("role") === "combobox") return;
    var form = q.form, matches = [], ai = -1;
    var list = document.createElement("div");
    list.id = "edan-find-list";
    list.className = "edan-find-list";
    list.setAttribute("role", "listbox");
    list.setAttribute("aria-label", "Matching districts");
    form.appendChild(list);
    q.setAttribute("role", "combobox");
    q.setAttribute("aria-autocomplete", "list");
    q.setAttribute("aria-expanded", "false");
    q.setAttribute("aria-controls", list.id);

    if (!findNames) {
      fetch(new URL("district_names.json", form.action))
        .then(function (r) { return r.json(); })
        .then(function (n) { findNames = n; if (q.value) search(); })
        .catch(function () {});
    }
    function hay(d) { return (d[0] + " " + d[1] + " " + d[3] + " " + d[2]).toLowerCase(); }
    function close() {
      list.style.display = "none";
      q.setAttribute("aria-expanded", "false");
      q.removeAttribute("aria-activedescendant");
    }
    function search() {
      var s = q.value.toLowerCase().trim();
      ai = -1;
      if (!s || !findNames) { matches = []; close(); return; }
      // Names that start with what was typed come first, then any word that starts with it.
      function rank(h) { return h.indexOf(s) === 0 ? 0 : h.indexOf(" " + s) >= 0 ? 1 : 2; }
      matches = findNames.filter(function (d) { return hay(d).indexOf(s) >= 0; })
        .sort(function (x, y) { return rank(hay(x)) - rank(hay(y)); }).slice(0, 12);
      list.textContent = "";
      matches.forEach(function (d, i) {
        var el = document.createElement("div"), county = document.createElement("span");
        el.setAttribute("role", "option");
        el.id = "edan-find-opt-" + i;
        el.dataset.i = i;
        el.textContent = d[0] + " ";
        county.className = "edan-find-county";
        county.textContent = "\u00b7 " + d[1] + " County";
        el.appendChild(county);
        list.appendChild(el);
      });
      if (!matches.length) {
        // Say so, rather than leave the reader wondering whether the search ran.
        var none = document.createElement("div");
        none.className = "edan-find-none";
        none.setAttribute("role", "status");
        none.textContent = "No district or county matches \u201c" + q.value.trim() + "\u201d.";
        list.appendChild(none);
      }
      // The list floats over the page, so put it right under the field it belongs to.
      list.style.top = q.offsetTop + q.offsetHeight + 6 + "px";
      list.style.left = q.offsetLeft + "px";
      list.style.width = q.offsetWidth + "px";
      list.style.display = "block";
      q.setAttribute("aria-expanded", "true");
    }
    function pick(i) {
      if (!matches[i]) return;
      q.value = matches[i][0];
      close();
      window.location.href = new URL("?district=" + encodeURIComponent(matches[i][2]), form.action).href;
    }
    q.addEventListener("input", search);
    q.addEventListener("focus", function () { if (q.value) search(); });
    q.addEventListener("keydown", function (e) {
      if (list.style.display !== "block" || !matches.length) return;
      var items = Array.prototype.slice.call(list.children);
      if (e.key === "ArrowDown") { ai = Math.min(ai + 1, items.length - 1); e.preventDefault(); }
      else if (e.key === "ArrowUp") { ai = Math.max(ai - 1, 0); e.preventDefault(); }
      else if (e.key === "Enter") { e.preventDefault(); pick(ai < 0 ? 0 : ai); return; }
      else if (e.key === "Escape") { close(); return; }
      else return;
      items.forEach(function (el, i) {
        el.classList.toggle("active", i === ai);
        el.setAttribute("aria-selected", i === ai ? "true" : "false");
      });
      q.setAttribute("aria-activedescendant", "edan-find-opt-" + ai);
      items[ai].scrollIntoView({ block: "nearest" });
    });
    // mousedown, so the pick lands before the field loses focus and the list closes.
    list.addEventListener("mousedown", function (e) {
      var d = e.target.closest("[data-i]");
      if (d) { e.preventDefault(); pick(+d.dataset.i); }
    });
    q.addEventListener("blur", function () { setTimeout(close, 150); });
    // The button with one clear match opens it; anything else goes to the lookup as a search.
    form.addEventListener("submit", function (e) {
      var v = q.value.trim().toLowerCase();
      var exact = (findNames || []).filter(function (d) { return d[0].toLowerCase() === v; })[0];
      if (exact) { e.preventDefault(); matches = [exact]; pick(0); }
      else if (matches.length === 1) { e.preventDefault(); pick(0); }
    });
  }

  /* ---- Light and dark: fade between them --------------------------------- */
  // A flip from a dark page to a bright one is a jolt. Where the browser can cross-fade the
  // whole page, the switch is held for a moment and made inside that fade.
  function initTheme() {
    if (prefersReduced || !document.startViewTransition) return;
    var labels = document.querySelectorAll('label.md-header__button[for^="__palette"]');
    Array.prototype.forEach.call(labels, function (label) {
      if (label.dataset.edanFade) return;
      label.dataset.edanFade = "1";
      label.addEventListener("click", function (e) {
        var input = document.getElementById(label.getAttribute("for"));
        if (!input) return;
        e.preventDefault();
        var fade = document.startViewTransition(function () {
          input.checked = true;
          input.dispatchEvent(new Event("change", { bubbles: true }));
        });
        // The browser may skip the fade (a hidden tab, a second press mid-fade). The switch
        // itself has still happened, so there is nothing to report.
        [fade.ready, fade.finished].forEach(function (p) { if (p) p.catch(function () {}); });
      });
    });
  }

  /* ---- Phone menu: it follows the finger ---------------------------------- */
  // Drag the open menu to the left and it moves with the finger. Let go and it carries on at
  // the speed of the hand: far or fast enough and it shuts, otherwise it settles back open.
  // It can be caught again at any point on the way.
  function spring(response, damping) {      // response in seconds; damping 1 settles with no bounce
    var w = (2 * Math.PI) / response;
    return {
      x: 0, v: 0, to: 0,
      step: function (dt) {
        for (var n = Math.ceil(dt / 0.004), h = dt / n; n > 0; n--) {
          this.v += (-w * w * (this.x - this.to) - 2 * damping * w * this.v) * h;
          this.x += this.v * h;
        }
        return Math.abs(this.x - this.to) < 0.4 && Math.abs(this.v) < 8;   // true once it has settled
      }
    };
  }
  function initDrawer() {
    var toggle = document.querySelector('[data-md-toggle="drawer"]');
    var panel = document.querySelector(".md-sidebar--primary");
    var scrim = document.querySelector(".md-overlay");
    if (!toggle || !panel || !scrim || panel.dataset.edanSwipe) return;
    panel.dataset.edanSwipe = "1";

    var width = 0, x = 0, down = null, dragging = false, trail = [], frame = 0, last = 0, s = null;
    function isDrawer() { return toggle.checked && getComputedStyle(panel).position === "fixed"; }
    function place() {
      panel.style.transform = "translateX(" + x + "px)";
      scrim.style.opacity = Math.max(0, Math.min(1, x / width));
    }
    function hold() { panel.style.transition = scrim.style.transition = "none"; }
    function letGo() {                       // hand the menu back to the theme's own styles
      panel.style.transform = panel.style.transition = scrim.style.opacity = scrim.style.transition = "";
    }
    function stop() { if (frame) cancelAnimationFrame(frame); frame = 0; s = null; }
    function finish() {
      stop();
      if (x < width / 2) {
        // Shut. Uncheck first with the inline position still in place, so nothing jumps.
        toggle.checked = false;
        toggle.dispatchEvent(new Event("change", { bubbles: true }));
      }
      letGo();
    }
    function tick(now) {
      frame = 0;
      var done = s.step(last ? Math.min(0.034, (now - last) / 1000) : 1 / 60);
      last = now;
      x = Math.min(s.x, width + 12);         // never show a gap between the menu and the screen edge
      place();
      if (done) { x = s.to; finish(); } else frame = requestAnimationFrame(tick);
    }
    function start(e) {
      if (!isDrawer()) return;
      if (s) { hold(); stop(); }             // caught mid-flight: it stays where it is, under the finger
      else { width = panel.offsetWidth; x = width; }
      down = { id: e.pointerId, x: e.clientX, y: e.clientY, from: x };
      dragging = false; trail = [];
    }
    function move(e) {
      if (!down || e.pointerId !== down.id) return;
      var dx = e.clientX - down.x, dy = e.clientY - down.y;
      if (!dragging) {
        // Wait for a clear sideways move, so a tap or an up-and-down scroll is left alone.
        if (Math.abs(dx) < 10 || Math.abs(dx) < Math.abs(dy)) return;
        dragging = true; hold();
        try { e.target.setPointerCapture(e.pointerId); } catch (err) {}
      }
      var raw = down.from + dx, over = raw - width;
      // Past fully open, it follows less and less instead of stopping dead.
      x = over > 0 ? width + (over * width * 0.55) / (width + 0.55 * over) * 0.25 : Math.max(-20, raw);
      place();
      trail.push([e.timeStamp, e.clientX]);
      while (trail.length > 2 && e.timeStamp - trail[0][0] > 100) trail.shift();
    }
    function end(e) {
      if (!down || e.pointerId !== down.id) return;
      var wasDragging = dragging;
      down = null; dragging = false;
      if (!wasDragging) return;
      var a = trail[0], b = trail[trail.length - 1], dt = a && b ? (b[0] - a[0]) / 1000 : 0;
      var v = b && e.timeStamp - b[0] < 80 && dt > 0 ? (b[1] - a[1]) / dt : 0;   // px per second at release
      // Where that speed would carry it decides open or shut, not where the finger happened to stop.
      var shut = x + (v / 1000) * 0.995 / (1 - 0.995) < width / 2;
      if (prefersReduced) { x = shut ? 0 : width; return finish(); }
      // Apple's own numbers for a sheet: quick, with a little give when it was thrown shut.
      s = spring(0.3, shut ? 0.8 : 1);
      s.x = x; s.v = v; s.to = shut ? 0 : width;
      last = 0; frame = requestAnimationFrame(tick);
    }
    [panel, scrim].forEach(function (el) {
      el.addEventListener("pointerdown", start);
      el.addEventListener("pointermove", move);
      el.addEventListener("pointerup", end);
      el.addEventListener("pointercancel", end);
    });
    // A drag that ends on the dimmed area must not also count as a tap that closes the menu.
    scrim.addEventListener("click", function (e) { if (s) e.preventDefault(); });
  }

  function init() {
    initSpotlight();
    initHome();
    initFind();
    initTheme();
    initDrawer();
  }

  // Material emits document$ on every (instant) navigation; otherwise run once.
  if (typeof window.document$ !== "undefined" && window.document$.subscribe) {
    window.document$.subscribe(init);
  } else if (document.readyState !== "loading") {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
