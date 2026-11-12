# Evaluator Retrieval Log (`scotus/9026000119` — `evt-petition-disposition` — `gemini-judge` — `20261111T154339Z`)

No corpus queries (`fedcourts query` / `fedcourts open-events`), CourtListener MCP calls, or web searches were performed.

To verify the three candidates' base-rate pooling against the statpack build in force when their predictions were placed (`run_id: 20261018T142134Z`, prior to the `sal-v8` statpack refresh), the local git-history statpack reconstruction helper was run for each alias:

- `uv run fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` -> resolved `build_sha: 886549a3ac32bdba039691b6d2ca7dc57bb72561` (`digest: sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`).
- `uv run fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` -> resolved `build_sha: 886549a3ac32bdba039691b6d2ca7dc57bb72561` (`digest: sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`).
- `uv run fedcourts statpack-at data/cases/scotus/9026000119/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` -> resolved `build_sha: 886549a3ac32bdba039691b6d2ca7dc57bb72561` (`digest: sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`).
