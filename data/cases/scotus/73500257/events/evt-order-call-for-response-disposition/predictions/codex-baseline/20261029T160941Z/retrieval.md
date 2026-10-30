# Retrieval beyond the provisioned case inputs

No lookup sought this petition's own disposition, post-baseline docket, or subsequent history. The supplied case documents were read locally. No other cell's output or topic-label artifact was read.

## Committed base rates and independent arithmetic check

Read the modern discretionary-cert, originating-circuit, paid-segment relist/CVSG/amicus, and sal-v4 prior-Term segment sections of `metrics/statpack.md`, with unrounded segment data in `metrics/statpack.json`. A read-only subagent independently checked those same two files, with no external calls and no edits. It reported the prior-Term baseline anchor, and a local `jq` aggregation independently confirmed 607/11,599 = 0.05233209759462023. No subagent supplied case-specific facts or another prediction.

## Corpus calls, including failures

Successful invocations used `UV_CACHE_DIR=/tmp/uv-cache` because the default UV cache is read-only.

1. `uv run fedcourts paths --court scotus --docket 73500257 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` initially failed before execution because `/home/codexcell/.cache/uv` was read-only. Reissued each with the temporary cache; path resolution and help succeeded. Help was read again in a tail-filtered invocation for the remaining options. No case data or transfer line came from these utility calls.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 4`: no rows returned.

   `ranged corpus reads: 902 GET(s), 236060672 byte(s)`

3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`: failed with `ValueError: the service backend has no client-side connection`. No vintage was returned; no transfer line was printed. I did not pull or modify the corpus.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '571 U.S. 3' --limit 1`: no rows; the diagnostic said only 200 scoped rows carried reporter citations and warned that empty citation matches are likely a coverage gap. No finding about Stanton's existence or holding was inferred.

   `ranged corpus reads: 4 GET(s), 1048576 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 3`: returned RiseandShine Corporation v. PepsiCo (24-1016), Devin Chaney v. United States (24-6543), and Monsanto Company v. Durnell (24-1068). None is this case, and none supplied a useful policing/immunity analogue. The term mask admitted older docket-number Terms with later grant dates; I did not treat these rows as a strictly pre-July-2026 decision set. No opinion bodies were requested or returned.

   `ranged corpus reads: 41 GET(s), 10747904 byte(s)`

The cell is forward mode and `DECIDED_BEFORE` was unset. The final query's 2025 Term restriction was an additional conservative choice, not an assertion that docket-number Term equals decision date.

## Web attempts

1. One `web.run` call searched `site.supremecourt.gov opinions Rivas Villegas Cortesluna 2021 per curiam qualified immunity` and `site.supremecourt.gov opinions "Zorn" "Linton" 2026`. The tool returned no usable result payload.
2. One `web.run` call searched `Rivas-Villegas Cortesluna 595 U.S. 1 2021 Supreme Court opinion`. Again there was no usable result payload.

No webpage or opinion text was obtained through these calls. They supplied no factual input. The petition's Zorn reference was not independently verified or used as an additional verified precedent.

## CourtListener MCP attempt

`search(type="o", case_name="Zorn v. Linton", court="scotus", num_results=2, fields=["caseName", "dateFiled", "citation", "cluster_id", "absolute_url", "opinions"])` returned HTTP 429, daily quota exhausted, with an estimated availability delay of 7,095 seconds. No opinion or result metadata was received. I stopped MCP retrieval and did not use a direct REST fallback or seek credentials.
