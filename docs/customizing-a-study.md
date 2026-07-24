# Customizing a Study

The fixture computes the expected number of occupied options after independent uniform
choices. Replace it rather than layering a second model beside it.

1. Implement deterministic analysis in `src/study/analysis.py`. Accept the configured
   seed even if the first model is exact, and return JSON-serializable values.
2. Implement one evaluator per executable claim in `src/study/claims.py`. Compare
   against registered expectations and tolerances; do not embed publication prose.
3. Replace the fixture record in `research/claims.yml`. Give every claim a stable ID,
   calibrated status, scope, limitations, and public visibility decision.
4. Add focused tests under `tests/`. Exact computations should test exact values;
   numerical methods should test controls, tolerances, and reproducibility.
5. Run `paperkit build` twice when changing generation logic. The artifact snapshots
   should remain byte-identical for the same inputs.

Extend `src/paperkit/pipeline.py` when the study needs new shared tables, figures, or
JSON views. Generate them once under `artifacts/`; reference those outputs from LaTeX
and Astro. Exploratory notebooks may inform a study but cannot be its only released
evidence.
