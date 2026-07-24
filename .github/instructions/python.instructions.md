---
description: "Deterministic Python rules for study code, claim evaluators, and generated evidence."
applyTo: "{src,scripts,tests}/**/*.py"
---

- Keep reusable workflow machinery in `src/paperkit/` and study logic in `src/study/`.
- Return structured results from analysis; do not scrape console output.
- Use exact arithmetic when practical and document floating tolerances otherwise.
- Seed every stochastic path from project metadata and report uncertainty for simulations.
- Add a focused test for every claim evaluator and contract change.
- Write generated output atomically and deterministically.
