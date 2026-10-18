"""MkDocs hook: a "Page updated" line under the title of every page but the home page.

People judging a health or advocacy site look for how current it is, so each page says when
it last changed. The date is the newest commit to the page's own Markdown file or to any
chart, lookup or picture it embeds (an iframe or img src), so a page whose chart was rebuilt
shows the rebuild. It needs the full git history, which is why the deploy workflow checks
out with fetch-depth: 0. Without git, or for a file never committed, the line is left out.
"""
import datetime
import os
import posixpath
import re
import subprocess
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@lru_cache(maxsize=None)
def last_commit(path):
    """Date of the newest commit that touched path, or None."""
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", path], cwd=ROOT,
                             capture_output=True, text=True, timeout=20).stdout.strip()
        return datetime.date.fromisoformat(out) if out else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def on_page_content(html, page, config, files):
    if page.is_homepage or "</h1>" not in html:
        return html
    docs = config["docs_dir"]
    paths = [os.path.join(docs, page.file.src_path)]
    here = posixpath.dirname("/" + page.url + "x")            # the folder the page is served from
    for ref in re.findall(r'<(?:iframe|img)\b[^>]*?\bsrc="([^"#?]+)', html):
        if "://" in ref or ref.startswith(("//", "data:")):
            continue
        site_path = posixpath.normpath(posixpath.join(here, ref)).lstrip("/")
        paths.append(os.path.join(docs, *site_path.split("/")))
    dates = [d for d in (last_commit(os.path.relpath(p, ROOT)) for p in paths if os.path.exists(p)) if d]
    if not dates:
        return html
    d = max(dates)
    line = (f'<div class="edan-updated">Page updated <time datetime="{d.isoformat()}">'
            f'{d:%B} {d.day}, {d.year}</time></div>')
    return html.replace("</h1>", "</h1>\n" + line, 1)
