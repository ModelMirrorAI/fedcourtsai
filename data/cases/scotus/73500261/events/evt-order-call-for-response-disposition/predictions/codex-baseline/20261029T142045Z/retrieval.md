# Retrieval record

No search sought this petition's disposition, later docket entries, or subsequent case coverage. No other cell's output or question-topic measurement artifact was read. The supplied July 28 snapshot and staged filings are the case-specific evidence.

## Committed context and local operations

- Read the modern-cert disposition section, paid-segment relist, CVSG and amicus sections, and sal-v4 per-Term band table in metrics/statpack.md. Read the matching state prefix rates and denominators from metrics/statpack.json. Pooled only OT2017–OT2024: 94/395 = 0.2379746835. The pack is the committed checkout's historical context, not a refreshed census.
- Ran `uv run fedcourts paths --court scotus --docket 73500261 --event evt-order-call-for-response-disposition --role predictor`. The first attempt failed because uv's default cache was read-only. Repeated successfully with a temporary uv cache. The output resolved the case, corpus and event paths and withheld the outcome as evaluator-only. No outcome file was opened.
- Read schema contracts, path/serialization helpers, and CLI help for validation and corpus querying. These were operational reads, not additional case facts.

## Web attempts

1. One web search call containing both queries:
   - `site.supremecourt.gov opinions 21pdf Kennedy Bremerton 21-418 history tradition Stone Graham`
   - `site.supremecourt.gov opinions 24pdf Mahmoud Taylor 24-297`
   The tool message exposed no usable result text. No numerical adjustment or independent doctrinal conclusion rests on these attempts.
2. Open attempt for the official Kennedy opinion at `https://www.supremecourt.gov/opinions/21pdf/21-418_i425.pdf`. No usable document text was returned in the tool message.
3. Open attempt for the official Mahmoud opinion at `https://www.supremecourt.gov/opinions/24pdf/24-297_4f14.pdf`. No usable document text was returned in the tool message.

## CourtListener MCP

1. `search(type="o", citation="449 U.S. 39", num_results=1, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions"])`, seeking Stone v. Graham, not this case. Returned HTTP 429, daily rate limit exceeded, with an approximately 262-second retry estimate. No opinion was retrieved. No REST fallback or token access was attempted.

## Corpus queries

Read `uv run fedcourts query --help` before querying; a second help display widened the terminal to expose the relevant options. All successful uv invocations used `UV_CACHE_DIR=/tmp/fedcourts-uv-cache`.

1. `uv run fedcourts query --court scotus --citation '597 U.S. 507' --decided-before 2025 --limit 2`
   - Intended known precedent: Kennedy v. Bremerton School District.
   - Returned no rows; a coverage note explained that only 200 scoped SCOTUS rows carry any citation and an empty lookup is more likely incomplete citation coverage than a nonexistent case. I did not read the empty result as evidence about precedent.
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
2. `uv run fedcourts query --court scotus --disposition granted --era 2010s --decided-before 2025 --limit 2`
   - Returned historical identifiers `scotus/62150023` (No. 19-896) and `scotus/61595192` (No. 19-1401). No opinion text was requested or returned. Neither is a matched classroom-religion or conditional-petition comparator; neither changed the probability, and no rate was estimated from the grant-selected rows.
   - Stderr: `ranged corpus reads: 180 GET(s), 47185920 byte(s)`.

No further retrieval was attempted. In particular, I did not look up the present state of Nathan, the response to this petition, or any disposition of No. 25-1360.
