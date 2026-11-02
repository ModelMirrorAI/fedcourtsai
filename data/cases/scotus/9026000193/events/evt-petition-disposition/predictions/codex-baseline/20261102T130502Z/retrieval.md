# Retrieval record

## Local reference material

Read the prediction contract and output schemas, the provisioned event, snapshot, context, same-question index and document manifest, and the staged QP, petition (including selected substantive sections and the bound lower-court opinion), BIO and reply. Read `metrics/statpack.md`, particularly modern cert dispositions, originating circuits, paid-segment relist/CVSG/amicus cuts, and the sal-v6 per-Term band table. No evaluator outcome, other cell output, or topic-labeling artifact was read.

## Corpus calls

1. `uv run fedcourts query --help` (also displayed a narrower help excerpt with `COLUMNS=120`): successful CLI reference read. All successful uv commands used `UV_CACHE_DIR=/tmp/uv-cache` and `--no-sync`; neither changes retrieval filters.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '540 U.S. 712' --limit 1`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - No rows. The CLI reported that only 200 in-scope rows carry reporter citations and cautioned that this is sparse coverage, not evidence that Locke does not exist. Did not retry this sparse corpus filter.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`
   - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Three granted comparators: U.S. DOGE Service (25-1103), Corey Duran Berry (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343). Returned distribution counts were 2, 5 and 2. No opinion bodies. The year mask is not a day-level cutoff; this is a forward cell with no replay clock, and these are not this petition. None supplied a substantive religious-funding analogy or a statistical grant-rate estimate.

## Web attempts

1. `web.run` search query: `site.supremecourt.gov opinions Carson Makin Locke training clergy 2022 20-1087`. The tool returned no usable result content. No case-outcome query was made.
2. `web.run` attempted to open `https://www.supremecourt.gov/opinions/21pdf/20-1087_dbfi.pdf`. No usable result content was returned. This attempted historical Carson locator had the wrong docket suffix; MCP subsequently identified Carson as 20-1088. The attempted page supplied no evidence.

## CourtListener MCP calls

1. `search(type="o", citation="540 U.S. 712", num_results=1, fields=["caseName","dateFiled","citation","absolute_url","opinions"])`: returned Locke v. Davey, decided February 25, 2004, cluster path `/opinion/131166/locke-v-davey/`, with combined-opinion ID 131166 and metadata/snippets identifying the majority and Scalia/Thomas dissents. Did not retrieve the full opinion.
2. `search(type="o", citation="596 U.S. 767", num_results=1, fields=["caseName","dateFiled","citation","absolute_url","opinions"])`: returned Carson v. Makin, decided June 21, 2022, combined-opinion ID 6351409, and the official slip-opinion locator ending `20-1088_dbfi.pdf`.
3. `search_document(opinion_id=6351409, query="vocational", snippet_size=1600)`: returned two overlapping excerpts from Carson's majority discussion retaining Locke's narrow treatment of vocational religious degrees and distinguishing general exclusion of religious schools. Used to check the BIO/reply's rival characterizations, not to retrieve anything about Hall's disposition.

## Operational note

The first `uv run fedcourts paths --court scotus --docket 9026000193 --event evt-petition-disposition --role predictor` failed because the default uv cache was read-only. Reissuing with `UV_CACHE_DIR=/tmp/uv-cache` and `--no-sync` succeeded. No dependencies were installed. The paths command names no outcome file for predictors. Final validation uses the same cache override and `UV_NO_SYNC=1`.
