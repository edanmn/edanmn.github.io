/* ==========================================================================
   embed.js — shared by the pages that sit inside iframes: the Plotly charts in
   docs/charts/, the district lookup and table, and the distance lookup.

   1. Follows the parent page's light/dark scheme (Material sets
      data-md-color-scheme on <body>), and keeps following it when the reader
      flips the toggle. Sets data-theme="dark|light" on <html> for CSS.
   2. Lets a lookup grow its iframe to fit its content, so there is no second
      scrollbar on a phone. Opt in with <html data-autoheight>.
   3. Re-themes Plotly charts for dark mode, and on narrow screens wraps the
      title and frees up room that fixed margins and colorbars take.

   Works when a page is opened on its own too: it then stays light unless the
   address ends in ?theme=dark.
   ========================================================================== */
(function () {
  "use strict";

  var root = document.documentElement;
  var host = null; // the parent document, when we are in a same-origin iframe
  try {
    if (window.parent !== window && window.parent.document.body) {
      host = window.parent.document;
    }
  } catch (e) {
    host = null;
  }

  function isDark() {
    var forced = new URLSearchParams(location.search).get("theme");
    if (forced) return forced === "dark";
    return !!host && host.body.getAttribute("data-md-color-scheme") === "slate";
  }

  /* ---- 2. Auto height ---------------------------------------------------- */
  function initAutoHeight() {
    if (!root.hasAttribute("data-autoheight") || !window.frameElement) return;
    var frame = window.frameElement;
    function fit() {
      // +4 covers the iframe's own border, so no inner scrollbar appears.
      frame.style.height = Math.ceil(document.body.getBoundingClientRect().height) + 4 + "px";
    }
    if ("ResizeObserver" in window) new ResizeObserver(fit).observe(document.body);
    window.addEventListener("load", fit);
    fit();
  }

  /* ---- 3. Plotly --------------------------------------------------------- */
  var DARK = {
    paper_bgcolor: "#16140f",
    plot_bgcolor: "#16140f",
    "font.color": "#e6e1d9"
  };
  var DARK_XY = {
    "xaxis.gridcolor": "#34302a",
    "yaxis.gridcolor": "#34302a",
    "xaxis.zerolinecolor": "#34302a",
    "yaxis.zerolinecolor": "#34302a"
  };
  var DARK_GEO = {
    "geo.bgcolor": "#16140f",
    "geo.landcolor": "#2a2620",
    "geo.lakecolor": "#1b2a36",
    "geo.subunitcolor": "#6b655c"
  };
  var NARROW = 520; // px; below this a chart is on a phone or in a narrow column

  function get(obj, path) {
    return path.split(".").reduce(function (o, k) {
      return o == null ? undefined : o[k];
    }, obj);
  }

  function wrapWords(text, perLine) {
    var lines = [""];
    String(text).split(" ").forEach(function (word) {
      var cur = lines[lines.length - 1];
      if (cur && (cur + " " + word).length > perLine) lines.push(word);
      else lines[lines.length - 1] = cur ? cur + " " + word : word;
    });
    return lines;
  }

  // What a chart needs changed on a narrow screen: {layout: {...}, traces: [{...}, ...]}.
  // `authored` holds the titles, x range and x type the chart was built with.
  function narrowPlan(gd, geo, authored) {
    var layout = {}, traces = [];
    var w = window.innerWidth;

    // Title: wrap it instead of letting it run off the edge.
    // ~7.4px per character at 15px; keep 16px clear each side.
    var lines = wrapWords(authored.title, Math.max(18, Math.floor((w - 32) / 7.4)));
    layout["title.text"] = lines.join("<br>");
    layout["title.font.size"] = 15;
    layout["margin.t"] = 30 + 20 * lines.length;
    // Fixed side margins were sized for a wide screen. Plotly's automargin still
    // makes room for whatever the axis labels need.
    layout["margin.l"] = geo ? 0 : 8;
    layout["margin.r"] = geo ? 0 : 12;

    // Axis titles: smaller, and wrapped to the room the axis has.
    if (authored.xtitle) {
      layout["xaxis.title.text"] = wrapWords(authored.xtitle, Math.floor((w - 70) / 6.6)).join("<br>");
      layout["xaxis.title.font.size"] = 12;
    }
    if (authored.ytitle) {
      layout["yaxis.title.text"] = wrapWords(authored.ytitle, Math.floor((window.innerHeight - 170) / 6.6)).join("<br>");
      layout["yaxis.title.font.size"] = 12;
    }

    var hbar = false, legend = false;
    (gd.data || []).forEach(function (t) {
      var u = {};
      var bar = t.type === "choropleth" ? "colorbar"
        : t.marker && t.marker.showscale ? "marker.colorbar" : null;
      if (bar) {
        // A colorbar with its title beside it takes a third of a phone screen.
        u[bar + ".thickness"] = 10;
        u[bar + ".len"] = 0.6;
        u[bar + ".xpad"] = 2;
        u[bar + ".title.side"] = "right";
        u[bar + ".title.font.size"] = 11;
        u[bar + ".tickfont.size"] = 11;
      }
      if (t.type === "bar" && t.orientation === "h") {
        hbar = true;
        // Let value labels sit outside the bars without being cut off.
        if (t.textposition === "outside") u.cliponaxis = false;
      }
      if (t.name && t.showlegend !== false && (gd.data || []).length > 1) legend = true;
      traces.push(u);
    });

    if (hbar) {
      // Long category labels squeeze the bars: wrap them and shrink the type.
      var cats = [];
      (gd.data || []).forEach(function (t) {
        if (t.type === "bar" && t.orientation === "h") {
          (t.y || []).forEach(function (c) { if (cats.indexOf(c) < 0) cats.push(c); });
        }
      });
      layout["yaxis.tickmode"] = "array";
      layout["yaxis.tickvals"] = cats;
      layout["yaxis.ticktext"] = cats.map(function (c) {
        return wrapWords(c, 20).join("<br>");
      });
      // Many rows leave less height per label.
      layout["yaxis.tickfont.size"] = cats.length > 15 ? 10 : 11;
      // With a fixed range the outside labels have nowhere to go, so widen it.
      // A log axis and an automatic range are left alone.
      if (authored.xrange && authored.xtype !== "log") {
        layout["xaxis.range"] = [authored.xrange[0], authored.xrange[1] * 1.45];
      }
    }
    if (legend && authored.showlegend !== false) {
      layout["legend.orientation"] = "h";
      layout["legend.y"] = -0.18;
      layout["legend.yanchor"] = "top";
      layout["legend.x"] = 0;
      layout["legend.font.size"] = 11;
      // Two columns, so a long legend does not crowd out the plot.
      layout["legend.entrywidthmode"] = "fraction";
      layout["legend.entrywidth"] = 0.5;
    }
    return { layout: layout, traces: traces };
  }

  function snapshot(obj, keys) {
    var out = {};
    keys.forEach(function (k) {
      var v = get(obj, k);
      out[k] = v === undefined ? null : v;
    });
    return out;
  }

  function themePlot(gd) {
    var types = (gd.data || []).map(function (t) { return t.type || "scatter"; });
    var geo = types.some(function (t) { return t === "choropleth" || t === "scattergeo"; });
    var colors = Object.assign({}, DARK, geo ? DARK_GEO : DARK_XY);

    // Remember what the chart was authored with, once, so light mode and wide
    // screens get it back exactly.
    if (!gd._edan) {
      var authored = {
        title: get(gd.layout, "title.text") || "",
        xrange: (get(gd.layout, "xaxis.range") || null) && get(gd.layout, "xaxis.range").slice(),
        xtype: get(gd.layout, "xaxis.type"),
        xtitle: get(gd.layout, "xaxis.title.text"),
        ytitle: get(gd.layout, "yaxis.title.text"),
        showlegend: get(gd.layout, "showlegend")
      };
      var plan = narrowPlan(gd, geo, authored);
      gd._edan = {
        narrow: false,
        authored: authored,
        colors: snapshot(gd.layout, Object.keys(colors)),
        layout: snapshot(gd.layout, Object.keys(plan.layout)),
        traces: (gd.data || []).map(function (t, i) {
          return snapshot(t, Object.keys(plan.traces[i]));
        })
      };
      // What the chart looks like as built: light, on a wide screen.
      gd._edan.sig = JSON.stringify(gd._edan.colors);
    }
    var saved = gd._edan;
    var dark = isDark();
    var narrow = window.innerWidth < NARROW;
    var update = {};
    Object.keys(colors).forEach(function (k) {
      update[k] = dark ? colors[k] : saved.colors[k];
    });

    var P = window.Plotly;
    var chain = Promise.resolve();
    if (narrow || saved.narrow) {
      // The plan is rebuilt on every pass because title wrapping depends on width.
      var now = narrow ? narrowPlan(gd, geo, saved.authored) : { layout: saved.layout, traces: saved.traces };
      Object.keys(now.layout).forEach(function (k) { update[k] = now.layout[k]; });
      if (narrow !== saved.narrow) {
        now.traces.forEach(function (u, i) {
          if (Object.keys(u).length) {
            chain = chain.then(function () { return P.restyle(gd, u, [i]); });
          }
        });
      }
      saved.narrow = narrow;
    }
    // A redraw is slow, so skip it when nothing would change. On a wide screen in
    // light mode that is every call.
    var sig = JSON.stringify(update);
    if (sig === saved.sig) return chain;
    saved.sig = sig;
    return chain.then(function () { return P.relayout(gd, update); });
  }

  function themePlots() {
    if (!window.Plotly) return;
    Array.prototype.forEach.call(document.querySelectorAll(".plotly-graph-div"), function (gd) {
      if (gd.data) themePlot(gd);
    });
  }

  /* ---- 1. Scheme ----------------------------------------------------------- */
  function apply() {
    var dark = isDark();
    root.setAttribute("data-theme", dark ? "dark" : "light");
    root.style.colorScheme = dark ? "dark" : "light";
    if (document.querySelector(".plotly-graph-div")) {
      document.body.style.background = dark ? DARK.paper_bgcolor : "";
    }
    themePlots();
  }

  apply();
  initAutoHeight();
  window.addEventListener("load", apply);
  if (host && "MutationObserver" in window) {
    new MutationObserver(apply).observe(host.body, {
      attributes: true,
      attributeFilter: ["data-md-color-scheme"]
    });
  }
  var resizeTimer = null;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(themePlots, 150);
  });
})();
