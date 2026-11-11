# APA_awards: working rules

@../../shared/idiom/CORE.md

Voice, working rules and dataset terms follow Idiom (`CORE.md`, `DATASETS.md`, `house/`; private repo, normally linked at
`../../shared/idiom`). The import is harmless when the file is absent.

A SubScout story ("Close to home") on Norway's APA 2025 licensing round. Follow SubScout's
`styleguide/` (github.com/AdmcCarthy/SubScout) for voice, rules, language and performance.

- Narrative in `story.md`; numbers come only from `story.py` metrics (`{{ name | filter }}`); thresholds
  use `{{ N | param }}`. A build with warnings is not finished.
- Data in `data/` is produced by `scripts/` from Sodir FactMaps; don't hand-edit it.
- Build: `uv run subscout build . --out _site`. Visual and performance checks use SubScout's
  `scripts/snapshot.py` and `scripts/perf.py` (0 console errors, no long frames at 4x CPU throttle).
- SubScout is pinned by git tag in `pyproject.toml` (`[tool.uv.sources]`); bump the tag to upgrade.
- British English; Observed / Derived / Interpreted confidence levels.
