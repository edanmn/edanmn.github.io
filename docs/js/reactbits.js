/* ==========================================================================
   reactbits.js — modern/interactive layer for the EDAN textbook.
   Effects modelled on reactbits.dev (Scroll Reveal, Animated Content, Aurora,
   Gradient Text, Count Up, Spotlight Card), rebuilt in vanilla JS so they run
   in a static MkDocs Material build.

   Principles:
   - Content is fully usable without JS; this only adds polish.
   - Respect prefers-reduced-motion: no entrance motion, values shown final.
   - Re-run on every page via Material's document$ (navigation.instant).
   - Never hide content that is already on screen (no flash of hidden content).
   ========================================================================== */
(function () {
  "use strict";

  document.documentElement.classList.add("rb-ready");

  var prefersReduced = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  function isHomePage() {
    var p = location.pathname.replace(/index\.html$/, "").replace(/\/+$/, "");
    return p === "";
  }

  /* ---- Scroll Reveal / Animated Content --------------------------------- */
  function initReveal() {
    var root = document.querySelector(".md-content .md-typeset");
    if (!root) return;

    var blocks = Array.prototype.slice.call(root.children).filter(function (el) {
      var tag = el.tagName;
      // Tables are skipped: Material and extra.css style tables only via
      // table:not([class]), so adding any class strips their styling.
      return tag !== "SCRIPT" && tag !== "STYLE" && tag !== "HR" && tag !== "TABLE";
    });

    if (prefersReduced || !("IntersectionObserver" in window)) {
      // No motion: leave everything visible as-is.
      return;
    }

    var io = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("rb-in");
            obs.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.06 }
    );

    var vh = window.innerHeight || document.documentElement.clientHeight;
    blocks.forEach(function (el) {
      el.classList.add("rb-reveal");
      // Already on screen at load → show immediately (avoid FOUC).
      if (el.getBoundingClientRect().top < vh * 0.92) {
        el.classList.add("rb-in");
      } else {
        io.observe(el);
      }
    });
  }

  /* ---- Spotlight Card / hover lift -------------------------------------- */
  function initSpotlight() {
    var cards = document.querySelectorAll(
      ".md-content .md-typeset .admonition, " +
        ".md-content .md-typeset details"
    );
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

  /* ---- Count Up --------------------------------------------------------- */
  function animateCount(el) {
    if (el.dataset.rbCounted) return;
    el.dataset.rbCounted = "1";

    var raw = el.textContent.trim();
    var match = raw.match(/-?\d+(?:\.\d+)?/);
    if (!match) return;

    var target = parseFloat(match[0]);
    var decimals = (match[0].split(".")[1] || "").length;
    var prefix = raw.slice(0, match.index);
    var suffix = raw.slice(match.index + match[0].length);

    if (prefersReduced) return; // keep the authored value as-is

    var duration = 1400;
    var start = null;

    function frame(ts) {
      if (start === null) start = ts;
      var t = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
      var val = (target * eased).toFixed(decimals);
      el.textContent = prefix + val + suffix;
      if (t < 1) requestAnimationFrame(frame);
      else el.textContent = prefix + target.toFixed(decimals) + suffix;
    }
    requestAnimationFrame(frame);
  }

  function initCount() {
    // .edan-stat--static opts out: "7 in 10" must never read "3 in 10" on the way up.
    var stats = document.querySelectorAll(".md-content .edan-stat:not(.edan-stat--static)");
    if (!stats.length) return;
    if (!("IntersectionObserver" in window) || prefersReduced) return;

    var io = new IntersectionObserver(
      function (entries, obs) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCount(entry.target);
            obs.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.6 }
    );
    stats.forEach(function (el) {
      el.textContent = el.textContent; // ensure simple text node
      io.observe(el);
    });
  }

  /* ---- Aurora background + Gradient hero text (home only) ---------------- */
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

    var h1 = document.querySelector(".md-content .md-typeset h1");
    if (h1 && !prefersReduced) h1.classList.add("rb-gradient-text");
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
      if (!matches.length) { close(); return; }
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
      if (list.style.display !== "block") return;
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

  function init() {
    initReveal();
    initSpotlight();
    initCount();
    initHome();
    initFind();
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
