# Contributing

Changes must preserve the evidence architecture: study values originate in
`src/study/`, flow through `paperkit build`, and are consumed from `artifacts/` by the
paper and site. Do not duplicate scientific constants in publication code.

Before opening a pull request, run:

```bash
python -m ruff check .
python -m pytest
paperkit validate
paperkit build
npm ci --prefix site
npm run check --prefix site
npm run build --prefix site
npm run test:e2e --prefix site
```

Use `python -m pytest` so the tests run under the selected virtual environment. Keep
changes focused, deterministic, and covered at the narrowest useful level. Never invent
citations or mark a human gate approved on another person's behalf.
