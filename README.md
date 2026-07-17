# VALUE Study — TMUCRD Report

Regulatory approaches to Valproate across Asia-Pacific countries using OMOP-CDM.

## Layout

- **Root** (`app.json`, `index.html`, `shinylive/`) — the built [Shinylive](https://shiny.posit.co/py/docs/shinylive.html) static export, served directly via GitHub Pages.
- **`source/`** — the editable Shiny for Python app (`app.py`) and its data files. Edit here, then re-export with `shinylive export source .` to update the root deployment.

## Deploying updates

```bash
pip install shinylive
shinylive export source .
git add .
git commit -m "Update report"
git push
```
