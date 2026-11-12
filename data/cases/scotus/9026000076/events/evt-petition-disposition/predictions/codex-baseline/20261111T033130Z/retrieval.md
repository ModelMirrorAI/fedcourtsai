# Retrieval record

## Provisioned and local materials

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the tooling and flags schemas, the event definition, case-level `record/context.json`, `record/snapshots/2026-11-11.json`, the documents manifest and questions presented, relevant sections of the petition, opposition, reply and appendix, and `record/related/related.json` and `record/related/26-78.json`. Read the committed `metrics/statpack.md`, especially the frozen-band context and paid-segment relist, CVSG, amicus and capital cuts. No realized-outcome file, other cell output, or topic-label artifact was read.

## CLI setup and help

1. `uv run fedcourts paths --court scotus --docket 9026000076 --event evt-petition-disposition --role predictor` failed because `/home/codexcell/.cache/uv` was read-only. No retrieval result.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000076 --event evt-petition-disposition --role predictor` succeeded and identified the case/event paths. It did not expose an outcome path.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. Help was later inspected again using `COLUMNS=160 ... | head -65` and `COLUMNS=180 ... | head -48` to recover untruncated option descriptions. These are three help invocations total, with no corpus retrieval.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '577 U.S. 92' --era 2010s --limit 3`
   - Result: no rows. Diagnostic explained that only 195 scoped rows carry citations and an empty result likely reflects missing citation coverage. No conclusion about Hurst's existence or holding was drawn.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '589 U.S. 139' --era 2020s --limit 3`
   - Result: no rows, with the same sparse-citation diagnostic. Switched to CourtListener for the actual opinion rather than continuing sparse-filter retries.
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`
   - Returned Goldman Sachs Bank USA v. Brown (25-1408), U.S. DOGE Service v. United States District Court (25-1103), and Corey Duran Berry v. United States (25-7026), with stored distribution counts 4, 2, and 5. These are unrelated, outcome-selected grants, not matched constitutional-sentencing priors; none informed the grant estimate. The year filter uses derived year, not a strict decision-date boundary; this forward cell did not rely on it as a historical cutoff.
   - `ranged corpus reads: 34 GET(s), 8912896 byte(s)`

## CourtListener MCP

1. `search(type="o", court="scotus", citation="589 U.S. 139", num_results=2)` returned McKinney v. Arizona, decided February 25, 2020, cluster 4729776, opinion 4510103, and an unrelated Yale Oil result. Only McKinney was used. The returned metadata supplied its official Supreme Court PDF location.
2. `search_document(opinion_id=4510103, query="ultimate sentencing", snippet_size=1200)` returned one passage confirming McKinney's distinction between jury aggravator findings and judicial weighing/ultimate sentencing. This corroborated the central opposition argument, without resolving the distinct statutory-choice issue in Jackson.

## Web attempts

1. Search query: `site.supremecourt.gov opinions 2019 McKinney Arizona 18-1109 jury ultimate sentencing decision`. Tool returned no visible content; no evidence used.
2. Search query: `McKinney Arizona 2020 589 U.S. 139 jury sentencing opinion`. Tool returned no visible content; no evidence used.
3. Open attempt: `https://www.supremecourt.gov/opinions/19pdf/18-1109_5i36.pdf`, the official McKinney PDF identified by CourtListener. Tool returned no visible content; no PDF evidence used. McKinney was instead verified through the successful MCP passage lookup.

No search or query sought Jackson's Supreme Court disposition or later history. No own-case live docket was retrieved. All actual case-specific evidence came from the provisioned record.

## Validation

Cell validation uses `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000076/events/evt-petition-disposition/predictions/codex-baseline/20261111T033130Z`. This checks local output files, not external case evidence.
