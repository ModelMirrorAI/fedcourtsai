# Retrieval Log — `scotus/9526000499` (`evt-brief-response-disposition`)

## Corpus CLI Queries

1. `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 10`
   - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Checked recent 2020s SCOTUS applications in the corpus for structure and disposition patterns.

*(Note: Three initial `uv run fedcourts query` invocations with `--text` exited with CLI usage error code 2 before executing any corpus read.)*

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="ca5"`, `case_name="Cameron v. Devon Energy"`, `num_results=5`)
   - Confirmed the underlying Fifth Circuit docket/opinion entry (`Parish of Cameron v. Devon Energy`, No. 26-30505, Oct. 2026).
2. `mcp_courtlistener_search` (`type="o"`, `case_name="City of Brunswick v. Honeywell"`, `num_results=5`)
   - Confirmed the Eleventh Circuit opinion entry (`City of Brunswick v. Honeywell International, Inc.`, No. 23-13200, Aug. 3, 2026).

## Web Searches

- None.
