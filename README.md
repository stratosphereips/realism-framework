# Realism Framework Artifacts

Companion artifacts to the paper *"Realistic Enough for What? A Multidimensional
Framework for Evaluating Cyber Environments"* (Stratosphere Laboratory, CTU Prague).

This repository publishes, as a static website:

1. **Use cases**: realism-requirement profiles over 11 dimensions.
2. **Environments**: a preliminary evaluation of 13 cyber environments across the
   same 11 dimensions.
3. **Scorecard**: an interactive application that reports whether an environment is
   suitable for a given use case.

## What maps to what

- The 11 realism dimensions and their 115 sub-dimensions: `data/dimension_elements.json`.
- Dimension groups and short descriptions (home page): `data/dimensions.json`.
- Use-case requirement profiles (dimension level, plus sub-dimension level for UC-A1):
  `data/use_cases.json`.
- The 13-environment evaluation: `data/environments.json` (five further environments are
  documented in the source analysis but not evaluated here, for lack of a verifiable public link).
- The pages and radar charts are **generated** from those three files.

## Rebuild the site

Everything is generated from `data/` by a small Python pipeline. Within a python
environment with `matplotlib`, `numpy`, `jinja2`, `pytest`:

```bash
./build.sh          # validate data -> render figures -> generate pages -> run tests
```

## Preview locally

The scorecard app loads data with `fetch()`, which browsers block on `file://`, so
serve the site over HTTP:

```bash
python -m http.server 8000
# then open http://localhost:8000/index.html
```

## Licensing

- **Code** (scripts under `build/`, `assets/`, `tests/`): MIT (see `LICENSE`).
- **Data and generated pages**: CC BY 4.0 (see `LICENSE-data`).
