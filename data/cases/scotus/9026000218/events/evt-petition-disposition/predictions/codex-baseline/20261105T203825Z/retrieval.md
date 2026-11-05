# Retrieval record

## Provisioned and repository inputs

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, the event definition, the case-level November 5 snapshot and context, `documents.json`, questions presented, petition, portions of the appendix including the judgments and dissent below, and `same-question.json`. Consulted `metrics/statpack.md`, especially modern cert dispositions, paid-segment relist/CVSG/amicus cuts, and the sal-v7 prior-Term reached-rate table. No other cell's outputs, evaluations, realized outcome, or labeling-measurement artifacts were read.

## CLI attempts and corpus retrieval

1. `uv run fedcourts paths --court scotus --docket 9026000218 --event evt-petition-disposition --role predictor` — failed before execution because the default uv cache was on a read-only filesystem. No case retrieval occurred.
2. `uv run fedcourts query --help` — the same cache failure. No retrieval occurred.
3. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts paths --court scotus --docket 9026000218 --event evt-petition-disposition --role predictor` — succeeded and resolved case/event paths; did not read the evaluator-only outcome.
4. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --help` — succeeded. Repeated once with output piped to `sed -n '65,155p'` to inspect supported citation, disposition, era, date, and limit filters. Help calls retrieve no priors.
5. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --citation '577 U.S. 385' --limit 2` — returned no rows. Warned that only 200 scoped rows carry citations and the empty lookup likely reflects sparse own-citation coverage, not absence of Wearry.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
6. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 3` — returned Burford German Funding LLC v. financialright claims GmbH (25-1269), Roofing Designs by JR v. Royal American Construction (25-1367), and Pedro Jose Silva Ochoa v. United States (25-7569). The first two concern civil matters and the third was outside the paid scored segment; none supplies a substantive Brady analogue. Used only to cross-check the corpus's GVR vocabulary and distribution fields, not to estimate a conditional grant rate. The Term filter selected docket Terms before 2026; returned resolution dates were in October 2026, still before this forward prediction.
   - `ranged corpus reads: 30 GET(s), 7864320 byte(s)`

All successful uv commands used the existing environment with synchronization disabled. No package installation was attempted.

## Web attempts

1. One `web.run` search call with two queries: `site.supremecourt.gov opinions Wearry Cain 577 385 2016 Brady` and `site.supremecourt.gov Smith Cain 565 U.S. 73 Brady 2012 opinion`. The tool returned no usable result content or reference identifiers.
2. One `web.run` search for `Wearry v Cain 577 U.S. 385 Supreme Court per curiam March 7 2016`. Again no usable result content was returned.
3. One `web.run` open attempt at the historical-opinion candidate `https://www.supremecourt.gov/opinions/15pdf/14-10008_aplc.pdf`. No usable document or status text was returned. This attempted filename was not treated as verified or used as evidence.

These were historical doctrinal searches, not searches for Matthews's disposition. No substantive fact was taken from the empty web responses.

## CourtListener MCP

1. `search(type="o", citation="577 U.S. 385", num_results=2)` — located Wearry v. Cain, Supreme Court, March 7, 2016, cluster 3183098, opinion 3183080, docket 14-10008. Also returned an irrelevant 1983 district-court result, which was disregarded.
2. `read_document(opinion_id=3183080, chunk_index=0, chunk_size=17000)` — read the opinion's opening text, establishing the state-postconviction posture, nondisclosure allegations, and per curiam reversal. Historical context for the availability of summary correction, not an outcome lookup for the forecast case.

No live retrieval of this petition's docket, decision, subsequent history, or coverage was attempted. No outcome-revealing material about this petition surfaced.
