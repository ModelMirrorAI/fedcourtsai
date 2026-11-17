# Retrieval record

## Provisioned and committed inputs

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the tooling and flag schemas, and `metrics/statpack.md` (modern discretionary cert, originating-circuit, paid-segment relist/CVSG/amicus, and sal-v8 Term cuts). Case inputs were the event definition, `record/snapshots/2026-11-16.json`, `record/context.json`, the document manifest, questions presented, petition argument and available bound-appendix portions, lower-court-docket summary, the opening of the separately staged party-list appendix, both related snapshots, the related manifest, and the empty same-question list. All paths are under `data/cases/scotus/9026000292/` unless otherwise specified. No other prediction or evaluation was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000292 --event evt-order-cvsg-disposition --role predictor` failed before execution because the default uv cache was read-only. Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts paths --court scotus --docket 9026000292 --event evt-order-cvsg-disposition --role predictor`; it resolved the expected case/event paths and withheld the evaluator-only outcome path. No outcome was accessed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --help` succeeded. Re-read its opening/options with `COLUMNS=130` and later `COLUMNS=150` to inspect the structured filters. These were help reads, not corpus data calls.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --era 2020s --disposition granted --limit 4` returned four recent granted cert petitions. The visible results included Robinhood Markets v. Sodha (CVSG followed by a grant) and Mullin v. RAICES. These were a broad procedural context check, not substantive TRIA analogues or a representative rate estimate. The output display was truncated; no additional case-specific inference rests on undisplayed rows.

   `ranged corpus reads: 32 GET(s), 8323072 byte(s)`

4. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --citation '578 U.S. 212' --limit 1` (piped to `jq` for compact selected fields) returned no row. Its coverage note said only 195 SCOTUS rows in scope carry reporter citations and an empty result is likely a coverage gap. No inference of nonexistent precedent followed.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

The cell is forward, with `decided_before: null`; no replay-year mask was required. Neither corpus query requested this case or its disposition.

## CourtListener MCP calls

Only lower-court opinions and historical precedent were sought; no Supreme Court disposition search was made.

1. `search(type="o", court="ca2", case_name="Havlish", filed_before="2026-11-17", num_results=5)` with selected metadata fields returned four opinions: the August 26, 2025 panel case (cluster 10660852), March 19, 2026 en banc case (10811059), and two older Havlish cases. It warned that requested `snippet` metadata was unavailable.
2. `get_endpoint_item(endpoint_id="clusters", item_id=10660852, fields=["id","case_name","date_filed","sub_opinions","citations"])` identified panel opinion 11127439 and confirmed the judgment date.
3. `get_endpoint_item(endpoint_id="clusters", item_id=10811059, fields=["id","case_name","date_filed","sub_opinions"])` identified en banc opinion 11277807 and confirmed March 19, 2026.
4. `search_document(opinion_id=11127439, query="as of", snippet_size=1600)` returned 20 matches, including the panel's timing holding and the dissent. The tool response was display-truncated.
5. `read_document(opinion_id=11127439, chunk_index=[10,11,12], chunk_size=8000)` retrieved the immunity and timing analysis. The response was display-truncated, so I followed with smaller chunks.
6. `read_document(opinion_id=11127439, chunk_index=[33,34,35,36], chunk_size=3000)` retrieved majority pp. 49–55: the blocking rationale, its application, and the enumerated holdings. Some combined-response text was display-truncated; the majority's holdings and substantial rationale remained visible.
7. `read_document(opinion_id=11277807, chunk_index=0, chunk_size=11000)` retrieved the en banc order, identified the five dissenting judges and separate opinions, and showed the beginning of Sullivan's dissent. The display truncated part of the Nardini concurrence.
8. `read_document(opinion_id=11277807, chunk_index=2, chunk_size=2500)` retrieved Nardini's complete brief concurrence with Lohier, confirming its recognition-power focus.
9. `search(type="o", citation="45 F.4th 1340", num_results=1)` with selected metadata fields returned zero results.
10. `search(type="o", court="ca11", case_name="Stansell", filed_after="2022-01-01", filed_before="2023-01-01", num_results=3)` with selected metadata returned *Keith Stansell v. UBS Financial Services, Inc.*, August 23, 2022 (opinion 7802935; official PDF for No. 20-11736), and a separate July 2022 Stansell opinion. This recovered the relevant case despite the empty citation lookup.
11. `search_document(opinion_id=7802935, query="any point in time", snippet_size=1100)` returned no literal match; no inference was drawn from the absence.
12. `search_document(opinion_id=7802935, query="temporal", snippet_size=1300)` returned two excerpts, around pp. 15–17, confirming that prior terrorist ties can suffice and that the Eleventh Circuit rejected a mandatory execution-time instrumentality test. This informed the distinction between a real temporal disagreement and an identical-facts split.

## Web tool attempts

These calls produced no usable returned source text or source identifiers in the tool transcript. They supplied no fact, forecast, or outcome to the prediction:

1. Search batch: `site.ca11.uscourts.gov "45 F.4th 1340" Stansell`; `site.supremecourt.gov "Dole Food" "478" "2003"`.
2. Search batch: `site.ca11.uscourts.gov "Stansell" "1340"`; `site.supremecourt.gov "Dole Food" "instrumentality"`.
3. Open attempt: official Eleventh Circuit PDF at `https://media.ca11.uscourts.gov/opinions/pub/files/202011736.pdf`.
4. Find attempt on that official PDF URL for `at any point`.

CourtListener's copy of the Eleventh Circuit opinion, not those unsuccessful web attempts, supplied the precedent text used. No web search sought this petition's disposition, its subsequent history, or any forecast.
