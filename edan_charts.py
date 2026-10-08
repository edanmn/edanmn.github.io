#!/usr/bin/env python3
"""Shared by the chart build scripts (build_charts.py, build_initiative_charts.py).

A chart is a small page in docs/charts/ that holds a description of the chart as JSON and lets
docs/js/charts.js draw it, styled by docs/css/charts.css. There is no chart library, so a chart
is on screen as soon as its page is. The kinds of chart and what each needs are listed at the
top of docs/js/charts.js.

    from edan_charts import write_chart
    write_chart("my_chart.html", {"type": "bars", "title": "...", "rows": [...]})
"""
import html, json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "docs", "charts")

CHART_HTML = """<!doctype html>
<html lang="en" data-autoheight><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="stylesheet" href="../css/charts.css">
</head><body>
<figure id="chart"></figure>
<script>window.SPEC = __SPEC__;</script>
<script src="../js/charts.js"></script>
<script src="../js/embed.js"></script>
</body></html>
"""

def write_chart(name, spec, out=OUT):
    os.makedirs(out, exist_ok=True)
    page = (CHART_HTML.replace("__TITLE__", html.escape(spec["title"]))
            .replace("__SPEC__", json.dumps(spec, separators=(",", ":")).replace("</", "<\\/")))
    open(os.path.join(out, name), "w", encoding="utf-8").write(page)
    print("wrote charts/" + name)

def albers(lon, lat, lon0=-94.2, lat0=46.4, lat1=44.5, lat2=48.5):
    """Albers equal-area conic centred on Minnesota. Returns (east, north) in Earth radii."""
    rad = math.radians
    n = (math.sin(rad(lat1)) + math.sin(rad(lat2))) / 2
    c = math.cos(rad(lat1)) ** 2 + 2 * n * math.sin(rad(lat1))
    rho = lambda la: math.sqrt(c - 2 * n * math.sin(rad(la))) / n
    th = n * rad(lon - lon0)
    return rho(lat) * math.sin(th), rho(lat0) - rho(lat) * math.cos(th)

def county_paths(counties):
    """Each county of a GeoJSON collection as an SVG path, in a frame 1000 units wide.
    Returns ({county id: path}, the frame's height)."""
    shapes = {}
    for ft in counties["features"]:
        g = ft["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        shapes[ft["id"]] = [[albers(lon, lat) for lon, lat in ring] for poly in polys for ring in poly]
    every = [pt for rings in shapes.values() for ring in rings for pt in ring]
    x0, y1 = min(x for x, _ in every), max(y for _, y in every)
    k = 1000 / (max(x for x, _ in every) - x0)
    place = lambda x, y: (round((x - x0) * k, 1), round((y1 - y) * k, 1))
    paths = {fips: "".join("M" + "L".join("%g,%g" % place(x, y) for x, y in ring) + "Z" for ring in rings)
             for fips, rings in shapes.items()}
    return paths, round((y1 - min(y for _, y in every)) * k, 1)
