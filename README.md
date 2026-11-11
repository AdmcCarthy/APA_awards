# Close to home: APA 2025

A data story on Norway's APA 2025 licensing round: 56 production licences, announced 13 January 2026
and granted 20 March 2026 (Sodir round code `TFO2025`). Built with
[SubScout](https://github.com/AdmcCarthy/SubScout) as its first real test case.

**Live page:** https://admccarthy.github.io/APA_awards/

## How it is made

```
story.md     the narrative: steps, charts, tables, with every number as a {{ expression }}
story.py     the metrics those expressions use, and derived tables, computed from data/
data/        story inputs (simplified GeoJSON and JSON), built from Sodir FactMaps; header.json is the hero's
             synthetic seismic band (scripts/make_header.py, seismic_art), not Sodir data
scripts/     fetch and processing pipeline that rebuilds data/ from Sodir
```

The page reads as a scrolling article or plays as a deck (**Present** button). Every number in the
prose is computed from `data/` at build time and listed, with its method, source and confidence, in
the page's "Basis of analysis" appendix. The build fails on unknown metrics, missing sources or figures
without a confidence level, and CI also fails on warnings (for example, a number typed by hand).

## Build

```bash
uv sync
uv run subscout build . --out _site
uv run python -m http.server -d _site      # open http://localhost:8000
```

## Rebuild the data from Sodir

```bash
uv sync --group pipeline
uv run python scripts/fetch_sodir.py      # Sodir FactMaps REST -> data/raw/*.geojson (~50 MB, git-ignored)
uv run python scripts/build_data.py       # -> data/*.json (simplified, WGS84)
uv run python scripts/build_partners.py   # -> data/partners.json (line-ups at award, all APA rounds 2003-2025)
uv run pytest -q
```

## Assumptions

- "APA 2026 awards" is read as the awards made in 2026, which is the APA 2025 round.
- Sodir lists 56 licences under TFO2025; the ministry announced 57 offers. Counts follow Sodir.
- Partners and equity shares are the line-up at grant.
- Long-run partnership charts group companies by today's owner (`scripts/companies.py`).
- Geometry is ED50 (Sodir native), requested as WGS84. Distances are edge to edge in ETRS89-LAEA
  (EPSG:3035), in km.
- Operator colours follow SubScout's identity palette in a fixed order (not brand colours); operators
  beyond its five slots are grey.

## GitHub Pages

`.github/workflows/pages.yml` builds the story with SubScout and deploys `_site/` on pushes to `main`.

## Licence and acknowledgement

MIT License with Acknowledgement ([LICENSE](LICENSE)): the MIT terms plus one condition. Anything built with this work says so,
visibly and in plain words, and does not imply endorsement: "Built with APA awards by Adam McCarthy (https://github.com/AdmcCarthy/APA_awards)". The wording is custom, so
the licence is not OSI-approved. Sodir data are used under the Norwegian Licence for Open Government Data (NLOD 2.0); attribution lines are in the story's basis of analysis. Third-party data and vendored code keep their own terms.
