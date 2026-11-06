# Close to Home: APA 2025

A journalistic data narrative on Norway's APA 2025 licensing round: 56 production
licences, announced 13 Jan 2026 and granted 20 Mar 2026 (Sodir round code `TFO2025`).

The page is in `web/index.html`, a static D3 page that reads `web/data/*.json`.

## Rebuild

```bash
pip install -r requirements.txt
python scripts/fetch_sodir.py      # Sodir FactMaps REST -> data/raw/*.geojson (~50 MB, git-ignored)
python scripts/build_data.py       # -> web/data/*.json (simplified, WGS84, d3-oriented)
python -m pytest -q
cd web && python -m http.server    # open http://localhost:8000
```

## Assumptions

- "APA 2026 awards" is read as the awards made in 2026, which is the APA 2025 round.
  The APA 2026 round itself closed on 1 Sep 2026 and is due to be awarded in early 2027.
- Sodir lists 56 licences under TFO2025; the ministry announced 57 offers. Counts follow Sodir.
- Partners and equity shares are the line-up at grant.
- Geometry is ED50 (Sodir native), requested as WGS84. Distances are edge to edge in ETRS89-LAEA (EPSG:3035), in km.
- Operator colours are brand-derived hues re-stepped to pass CVD checks. They are not official brand values.

## GitHub Pages

`.github/workflows/pages.yml` builds `_site/` with `scripts/build_site.py` and deploys it with GitHub Actions.
The build script wraps the `web/index.html` fragment in a full HTML document.
The workflow runs on pushes to `main` or this branch that touch `web/`, and can also be started by hand.

One-time setup: go to **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
The site is then served at `https://<owner>.github.io/APA_awards/`.
