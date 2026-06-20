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
      return tag !== "SCRIPT" && tag !== "STYLE" && tag !== "HR";
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
        ".md-content .md-typeset details, " +
        ".md-content .md-typeset table:not([class])"
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
    var stats = document.querySelectorAll(".md-content .edan-stat");
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

  function init() {
    initReveal();
    initSpotlight();
    initCount();
    initHome();
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
