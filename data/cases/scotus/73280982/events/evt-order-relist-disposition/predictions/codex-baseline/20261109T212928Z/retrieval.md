# Retrieval record

## Provisioned and committed material

Read the prediction prompt, output schemas, event definition, `record/context.json`, `record/snapshots/2026-11-09.json`, document inventory, questions presented, and relevant sections of the petition, BIO, cert reply, SG invited brief, combined supplemental briefs, decision below, and lower-court docket. Read the modern-cert, paid relist/CVSG/amicus, and sal-v8 prior-Term segment tables in `metrics/statpack.md`. No other prediction, evaluation, outcome, or topic-label artifact was opened.

## CLI and corpus calls

1. `uv run fedcourts paths --court scotus --docket 73280982 --event evt-order-relist-disposition --role predictor` failed before execution because the default uv cache was read-only. No corpus content returned.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts paths --court scotus --docket 73280982 --event evt-order-relist-disposition --role predictor` succeeded and identified the event and corpus paths; it withheld the evaluator-only outcome path.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --help` was invoked three times, twice with output limited to the initial help sections. These were syntax inspections, not corpus reads.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --citation '601 U.S. 257' --limit 3` returned no matching row and warned that reporter-citation coverage is sparse. Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --docket-number 22-1165 --limit 1` returned Macquarie, case `scotus/68162458`, with a September 29, 2023 cert grant and a 2024 merits disposition. Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. Used as a related historical example, not as an estimate of an SG-supported grant rate.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts query --court scotus --docket-number 13-435 --limit 1` returned a sparse historical row, `scotus/2644090`, with no useful caption, disposition, or opinion text. Transfer: `ranged corpus reads: 720 GET(s), 188612608 byte(s)`. No substantive or quantitative inference taken from that row. This lookup was unexpectedly expensive.

The cell is forward mode; no replay clock was imposed. Neither corpus lookup sought this petition's disposition or subsequent history.

## Web requests

One batched `web.run` search attempted the queries `site.supremecourt.gov opinions 23pdf Macquarie Infrastructure Moab 601 257` and `site.supremecourt.gov opinions 14pdf Omnicare Laborers 575 175`. The tool exposed no usable search results. A subsequent `web.run` open of the historical Macquarie slip-opinion PDF at `https://www.supremecourt.gov/opinions/23pdf/22-1165_10n2.pdf` likewise exposed no usable text. No own-case search was performed, and no web-derived outcome or factual assertion entered the forecast.

## CourtListener MCP

1. `search(type="o", citation="601 U.S. 257", num_results=2)` returned two records of Macquarie's April 12, 2024 opinion, including cluster 10600103/opinion 11066691 and cluster 9493079/opinion 9959692. This was historical precedent, not the forecast case.
2. `search_document(opinion_id=11066691, query="Section 11", snippet_size=850)` returned two overlapping excerpts discussing Section 11's required-statements liability and its distinction from Rule 10b-5. Used to avoid overreading Macquarie as eliminating all pure-omission claims under Section 11.

No full opinion, other live docket, current own-case docket, or disposition coverage was retrieved. Local shell inspections and the required validation are operational checks, not additional case sources.
