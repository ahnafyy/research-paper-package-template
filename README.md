# Paper OS Package Template

An opinionated GitHub template for turning a small computational or theoretical
question into calibrated claims, reproducible evidence, an arXiv manuscript, and
an interactive explainer.

The repository treats research as a checked build. Scientific values originate in
`src/study/`; `paperkit build` evaluates registered claims and generates one evidence
bundle under `artifacts/`; the LaTeX paper and Astro site consume that bundle. Human
approval is required at scope, novelty, design, evidence, and release gates.

The checked-in project is intentionally an unpublishable fixture. It demonstrates an
exact occupancy calculation while `initialized: false`, `TODO` markers, and pending
gates prove that the release guard is active.

## Start a project

Use this repository as a GitHub template, clone the new repository, then run:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/init_project.py
```

The initializer records project metadata but does not approve research gates. Replace
the fixture in `src/study/`, register claims in `research/claims.yml`, and complete the
research records before requesting human approval.

## Build and inspect

Python 3.11 or newer is required. The site requires Node 22.12 or newer.

```bash
paperkit build
paperkit validate
python -m pytest
python -m ruff check .

npm ci --prefix site
npm run check --prefix site
npm run dev --prefix site
```

The site is served at `http://localhost:4321`. Its benchmark, results, and claim table
come from `artifacts/site-data.json`, not from a second implementation in TypeScript.

To stage generated manuscript inputs without TeX:

```bash
paperkit build-paper --stage-only
```

To compile `dist/paper.pdf`, install a TeX distribution containing `latexmk`, then run
`paperkit build-paper`.

## Release

Use a dry run while developing:

```bash
paperkit release --dry-run
```

A release remains blocked until metadata is initialized, placeholders are removed,
all executable claims pass, and a human approves every gate. A successful
`paperkit release` creates:

- `dist/paper.pdf`
- `dist/arxiv-source.tar.gz`
- `dist/reproducibility.zip`
- `dist/site/`
- `dist/CITATION.cff`
- `dist/SHA256SUMS`

GitHub Actions independently checks the evidence pipeline, manuscript, static site,
browser behavior, accessibility, and Pages deployment.

## Guides

- [Research cycle](docs/research-cycle.md)
- [Claim taxonomy](docs/claim-taxonomy.md)
- [Customizing a study](docs/customizing-a-study.md)
- [Publication and release](docs/publication-and-release.md)
- [Contributing](CONTRIBUTING.md)
