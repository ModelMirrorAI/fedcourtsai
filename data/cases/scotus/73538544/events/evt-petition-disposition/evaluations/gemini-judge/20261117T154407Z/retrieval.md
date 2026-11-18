# Retrieval Log (`scotus/73538544` — `evt-petition-disposition` — `gemini-judge` / `20261117T154407Z`)

No corpus queries (`fedcourts query` / `fedcourts open-events`), CourtListener MCP lookups, or web searches were performed beyond the provisioned inputs.

- Read committed `metrics/statpack.md` (header/scope verification) and reconstructed the placement statpack build active at each candidate's prediction run (`run_id: 20261029T180303Z`) via local git history:
  - `uv run fedcourts statpack-at data/cases/scotus/73538544/record/blinded/candidate-{a,b,c}/ --ref origin/main --out-dir /tmp/statpack-at/candidate-{a,b,c}` → `build_sha = 7bcde3b105cb212283905eda17b827efc188e80c` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `alternative_sha = null`).
