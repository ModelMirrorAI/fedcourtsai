# Retrieval record

- Read the committed `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-scored-segment relist and CVSG cuts, and the `sal-v4` per-Term salience table. Used only 2017–2025 rows for the numerical anchor. A local Python calculation pooled the displayed baseline reached rates and denominators, yielding approximately 5.0109% over weighted n=12,720. A metadata-key search in `metrics/statpack.json` returned no freshness information used in the forecast.
- `uv run fedcourts paths --court scotus --docket 9026000045 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only. Retried successfully with a writable temporary cache. This resolves paths only; no outcome file was opened.
- Web search: `site.supremecourt.gov opinions Axon Enterprise FTC 2023 21-86 express implicitly jurisdiction`. No usable result returned.
- Web search: `Axon Enterprise FTC April 14 2023 Supreme Court opinion 598 175`. No usable result returned.
- Attempted web opening of the Supreme Court opinion URL `https://www.supremecourt.gov/opinions/22pdf/21-86_l5gm.pdf`. No usable document returned; it supplied no evidence.
- CourtListener MCP `search(type="o", citation="598 U.S. 175", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url", "citation"])`: HTTP 429, 300/hour limit, retry indicated after 793 seconds. No opinion or search results returned. Did not retry or use direct REST.
- No `fedcourts query` or `open-events` call, hence no ranged-corpus transfer line. No live corpus blob read, no search for this petition's outcome, and no outcome-bearing material encountered.

Local prompt/schema reads and validation are contract checks, not additional case evidence.
