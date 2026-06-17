# Seizure-Safe Schools: An Intelligent Textbook

A plain-language, interactive textbook from the Epilepsy Data & Advocacy Network (EDAN). It
explains epilepsy, seizure first aid, and Minnesota's seizure-safety law (Minn. Stat. 121A.24),
and presents the data behind seizure-plan gaps in Minnesota schools. Built in the MkDocs
Material "intelligent textbook" style (interactive p5.js MicroSims, quizzes, glossary).

## Run it locally
```bash
pip install mkdocs mkdocs-material
cd textbook
mkdocs serve
# open http://127.0.0.1:8000
```

## Build a static site
```bash
mkdocs build      # outputs to ./site
```

## Publish to your personal github.io
1. Create a GitHub repo, e.g. `seizure-safe-schools`.
2. Push this `textbook/` folder as the repo root (mkdocs.yml is already set to your username).
3. Deploy either way:
   - One command: `mkdocs gh-deploy` (pushes the built site to the `gh-pages` branch), or
   - Automatic on every push: keep `.github/workflows/deploy.yml` (already included).
4. In the repo Settings > Pages, set the source to the `gh-pages` branch (if using gh-deploy)
   or to GitHub Actions (if using the workflow). Your site appears at
   `https://edanmn.org/`.

## Structure (mirrors the intelligent-textbooks pattern)
```
mkdocs.yml
docs/
  index.md
  chapters/00..06/index.md     (each chapter; some include quiz.md)
  sims/seizure-first-aid/       (p5.js MicroSim: main.html, sketch.js, index.md)
  glossary.md
  css/extra.css
.github/workflows/deploy.yml
```

## Source of the data
The chapter "The Data: Mapping the Gaps" is built from EDAN's audit of 328 Minnesota
districts (see the parent project's FINDINGS.md, RELIABILITY.md, and data/ folder).

This material is informational, not legal or medical advice.
