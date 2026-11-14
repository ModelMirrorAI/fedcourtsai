# Evaluator Retrieval Log

Beyond the stable prompt/schema inputs, the committed `metrics/statpack.md`, and the provisioned case files under `data/cases/scotus/73280982/events/evt-order-relist-disposition/` and `data/cases/scotus/73280982/record/`, the following read-only lookups were performed during evaluation:

1. **Canonical path check (`fedcourts paths`)**:
   - `uv run fedcourts paths --court "scotus" --docket "73280982" --event "evt-order-relist-disposition" --role evaluator`
   - Confirmed canonical `case_id`, `event`, and `outcome` paths.

2. **Prediction-time statpack reconstruction (`fedcourts statpack-at`)**:
   - `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
   - `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
   - `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
   - All three resolved to commit `ca0c9e1a49e292692bdc5b092cd9f868561169b8` (`statpack_digest: sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`, landed `2026-11-09T14:37:29+00:00`), used to verify each candidate's cited base-rate figures against the pack in force at `run_id: 20261109T212928Z`.

3. **Pre-relist summary inspection for leakage audit**:
   - Read `data/cases/scotus/73280982/summaries/2026-10-27.md` solely to audit `claude-baseline`'s logged shell read (`head -c 1500 summaries/2026-10-27.md`), confirming it was an undecided pre-relist case summary generated `2026-10-27T04:39:38Z` containing no outcome or prediction data.

No `fedcourts query` / `fedcourts open-events` corpus queries, CourtListener MCP calls, or external web searches were executed.
