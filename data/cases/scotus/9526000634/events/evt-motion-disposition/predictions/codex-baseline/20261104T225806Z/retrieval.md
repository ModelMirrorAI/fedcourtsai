# Retrieval log

## Local contract and provisioned inputs

Read `.github/prompts/predict.md`, the prediction/tooling/flags schemas, `event.yaml`, `record/context.json`, `record/snapshots/2026-11-04.json`, `record/documents/documents.json`, and the complete `application.txt`. No other prediction, evaluation, realized outcome, or topic-label artifact was read. Consulted the repository Justice roster for exact distribution labels.

## CLI and corpus calls, in order

All successful `uv run` commands below used `UV_CACHE_DIR=/tmp/fedcourts-uv-cache` after the initial default-cache failure. No packages were installed.

1. `uv run fedcourts paths --court scotus --docket 9526000634 --event evt-motion-disposition --role predictor` — failed before execution because the default uv cache was read-only. Retried successfully below.
2. `uv run fedcourts query --help` — succeeded and displayed structured filters and options.
3. `uv run fedcourts paths --court scotus --docket 9526000634 --event evt-motion-disposition --role predictor` — succeeded; confirmed case and event paths and that outcome is evaluator-only. No outcome was opened.
4. `uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 5` — rejected the invalid era `modern`, printed the accepted decade vocabulary, and returned no priors. No transfer line was shown.
5. `uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 5` — returned five denied cert petitions. The combined terminal response was truncated and its transfer line was not recoverable from the displayed response. The same query was rerun with compact output below; no transfer count is invented for this first execution.
6. `uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 5 | jq -c '{case_id,case_name,docket_number,disposition,application_kind,capital_case}'` — returned Google v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), O'Donnell v. Chicago (25-1098), Utah v. Mullins (25-1115), and Hadley v. South Bend (25-1158). All had null application kind and were not execution-stay comparators; no rate was inferred from this outcome-filtered sample.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

The committed `metrics/statpack.md` interim section and `metrics/statpack.json` interim per-Term fields were read. OT2016–OT2025 finer totals: 0 granted, 0 resolved, 1,366 unread, 16 unparsed. No valid finer-reading baseline; older registered counts were not substituted. No `open-events` or `fedcourts stats` call was attempted.

## Web calls

1. One `web.run` search call with queries `site.supremecourt.gov opinions Bucklew Precythe 2019 Baze substantial risk severe pain stay execution` and `site.supremecourt.gov Hill McDonough 2006 stay execution equity 547 573` — tool returned no usable result content. No inference was drawn.
2. One `web.run` search call with queries `site.supremecourt.gov "Hill v. McDonough" "stay"` and `site.supremecourt.gov "Bucklew" "recordkeeping"` — again no usable result content. No inference was drawn.

Neither search named Guardado or sought the disposition of this application.

## CourtListener MCP

1. `search(type="o", citation="547 U.S. 573", court="scotus", num_results=1)` — returned *Hill v. McDonough*, decided June 12, 2006, opinion 145647.
2. `search_document(opinion_id=145647, query="significant possibility", snippet_size=1200)` — returned the stay passage addressing merits likelihood, equitable discretion, State enforcement interests, and delay. Used as general legal context, not a quantitative prior.
3. `search(type="o", citation="553 U.S. 35", court="scotus", num_results=1)` — returned *Baze v. Rees*, decided April 16, 2008, including lead opinion 9435238 and combined opinion 145817.
4. `search_document(opinion_id=9435238, query="isolated", snippet_size=650)` — returned the plurality's distinction between an isolated mishap and a substantial risk of serious harm. Used as general legal context.

No CourtListener search targeted this case, its certiorari companion, or its subsequent history. Final local schema/cell validation uses the contract's `uv run fedcourts validate data --cell` command against this output directory; it is not retrieval of an outcome.
