#!/usr/bin/env python3
"""Finish the Plotly charts in docs/charts/ so they behave inside the site.

Plotly's full_html output has no mobile viewport tag and knows nothing about the
site's dark mode. This adds, to every chart that lacks them:
  - a viewport tag, so the chart is responsive inside its iframe on a phone
  - docs/js/embed.js, which follows the site's light/dark scheme and tidies the
    chart on narrow screens

build_charts.py and build_initiative_charts.py call finish_charts() after they write
their charts. It is safe to run again, and on its own:  python postprocess_charts.py
"""
import glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "docs", "charts")

VIEWPORT = '<meta name="viewport" content="width=device-width, initial-scale=1">'
EMBED = '<script src="../js/embed.js"></script>'

def finish_charts(out=OUT):
    changed = 0
    for fp in sorted(glob.glob(os.path.join(out, "*.html"))):
        t = old = open(fp, encoding="utf-8").read()
        if 'name="viewport"' not in t and "<head>" in t:
            t = t.replace("<head>", "<head>" + VIEWPORT, 1)
        if EMBED not in t and "</body>" in t:
            t = t.replace("</body>", EMBED + "\n</body>", 1)
        if t != old:
            open(fp, "w", encoding="utf-8").write(t)
            changed += 1
    print(f"charts finished: {changed} updated in {os.path.relpath(out, HERE)} (viewport + embed.js)")

if __name__ == "__main__":
    finish_charts()
