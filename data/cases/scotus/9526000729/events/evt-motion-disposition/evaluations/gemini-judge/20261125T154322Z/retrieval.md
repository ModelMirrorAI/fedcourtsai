# Evaluator Retrieval Log — `scotus/9526000729` (`evt-motion-disposition`)

Evaluator: `gemini-judge` (`RUN_ID = 20261125T154322Z`, `MODEL_ID = gemini-4-carbon`).

## 1. Provisioned Case & Blinded Candidate Files Inspected

- Stable contract and schemas: `.github/prompts/evaluate.md`, `schemas/evaluation.schema.json`, `schemas/agent_tooling.schema.json`, `schemas/agent_flags.schema.json`, `metrics/statpack.md`.
- Event & outcome record: `data/cases/scotus/9526000729/events/evt-motion-disposition/event.yaml`, `data/cases/scotus/9526000729/events/evt-motion-disposition/outcome.json`, `data/cases/scotus/9526000729/record/context.json`, `data/cases/scotus/9526000729/record/snapshots/2026-11-24.json`, `data/cases/scotus/9526000729/summaries/2026-11-21.md`, `data/cases/scotus/9526000729/summaries/2026-11-24.md`. (Verified `record/opinion/` and `record/documents/` absent, as expected on a summary chambers denial of a Rule 34.7 sealed stay application.)
- Blinded candidate directories (`record/blinded/gemini-baseline/`, `record/blinded/claude-baseline/`, `record/blinded/codex-baseline/`): read `prediction.json`, `reasoning.md`, `predicted_reasoning.md`, `retrieval.md`, and `retrieval_log.json` for each alias. Did **not** inspect `predictions/`, `blinding.json`, `config/predictors.yaml`, or `git log`.

## 2. `fedcourts` CLI Calls (Paths, Prediction-Time Statpack, and Corpus Spot-Checks)

1. `uv run fedcourts paths --court "scotus" --docket "9526000729" --event "evt-motion-disposition" --role evaluator`
   - Result: resolved `case_id = scotus/9526000729`, `corpus = corpus/corpus.db`, `event.yaml`, and `outcome.json`.
2. `uv run fedcourts statpack-at data/cases/scotus/9526000729/record/blinded/gemini-baseline/ --ref origin/main --out-dir /home/runner/.gemini/tmp/fedcourtsai/statpack-at/gemini-baseline`
   - Result: resolved `statpack_digest = sha256:a7d6f5cde0a4c0e9f80d0491dd08e65cd303aa7b14ce6ec1133e915c88af92a4` (shared by all three candidates) to commit `50244479fc2d73e7de2ccedfad5787bdd1b56f72` (`landed_at: 2026-11-20T18:59:23+00:00`), confirming all candidates' strictly-prior OT2016–OT2025 interim counts (`156/1,337`, `63/906`, `282/1,380`, `769/1,380`, `120/1,380`).
3. `uv run fedcourts query --court scotus --docket-number 26A715 --limit 2`
   - Stderr: `ranged corpus reads: 21 GET(s), 5439488 byte(s)`
   - Result: verified `scotus/9526000715` (*Rachel Beth Odom v. Oklahoma*, `date_decided: 2026-11-19`, `disposition: denied`, `interim_reading: denied`, `referred_to_court: false`, `response_requested: false`, `amicus_briefs: 0`).
4. `uv run fedcourts query --court scotus --docket-number 22A184 --limit 2`
   - Stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: verified `scotus/65348855` (*Yeshiva University v. YU Pride Alliance*, `amicus_briefs: 1`, `referred_to_court: true`, `response_requested: true`, `disposition: denied`).
5. `uv run fedcourts query --court scotus --docket-number 25A572 --limit 1`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (also queried in initial batch)
   - Result: verified `scotus/73279244` (*Ian Buenaventura v. Leslie Buot*, originating from Supreme Judicial Court of Maine `And-25-246`, pro se, `disposition: denied`, `referred_to_court: true` following April 2026 refiling, `date_decided: 2026-05-18`).
6. `uv run fedcourts query --court scotus --docket-number 26-5639 --limit 1`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (also queried in initial batch)
   - Result: verified `scotus/9026005639` (*Ian S. R. Buenaventura v. Leslie G. C. Buot*, originating from `And-25-246`, `date_filed: 2026-09-22`, `distributed_for_conference: 2026-12-04`).

## 3. CourtListener MCP & Public Docket Spot-Checks

1. `mcp_courtlistener_analyze_citations` on *Hollingsworth v. Perry*, 558 U.S. 183, 190 (2010); *Nken v. Holder*, 556 U.S. 418, 434 (2009); and *Ankenbrandt v. Richards*, 504 U.S. 689, 703 (1992).
   - Result: 3 of 3 verified (`cluster_id` 1747, 145884, and 112752).
2. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 71699259, ...})` and `mcp_courtlistener_call_endpoint(endpoint_id="parties", query={"docket": 71699259, ...})`
   - Result: verified District of Maine docket `2:25-mc-00465` (*In re Buenaventura*), listing `"ENJOINED FILER IAN R BUENAVENTURA"` and Judge Lance E. Walker's October 20, 2025 order denying leave to remove state divorce and child-custody proceedings under *Ankenbrandt v. Richards*, 504 U.S. 689, 703 (1992).
3. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/25a572.html` and `https://www.supremecourt.gov/docket/docketfiles/html/public/26a715.html`
   - Result: verified exact proceeding dates and order wording cited by `gemini-baseline` (`25A572` submitted Nov. 7, 2025, denied by Justice Jackson Nov. 17, 2025, refiled to Justice Alito Apr. 8, 2026, referred Apr. 22, 2026, denied by the Court May 18, 2026; `26A715` stay denied and motion to file under seal granted by Justice Gorsuch Nov. 19, 2026).
