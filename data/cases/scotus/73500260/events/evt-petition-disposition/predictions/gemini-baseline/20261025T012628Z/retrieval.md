# Retrieval Log (`scotus/73500260` — `evt-petition-disposition`)

## Corpus CLI Queries (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 73500260 --event evt-petition-disposition --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --court scotus --docket-number 21-1262`
   - Transfer: `ranged corpus reads: 6 GET(s), 1441792 byte(s)`
   - Retrieved prior related petition `scotus/72470586` (*TitleMax of Delaware, Inc., dba TitleMax, et al. v. Richard Vague, Secretary, Pennsylvania Department of Banking and Securities*, No. 21-1262, originating from CA3 No. 21-1020, distributed twice and denied on `2022-06-27`).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 16 GET(s), 4194304 byte(s)`
   - Retrieved recent 2020s granted SCOTUS rows for context.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Retrieved recent 2020s denied SCOTUS rows for context.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="TMX Finance Corporate Services v. Spicher"`, `num_results=10`) — returned 0 indexed opinion results (`query_id: b05b0073`).
2. `mcp_courtlistener_search` (`type="o"`, `case_name="TitleMax of South Carolina v. Spicher"`, `num_results=10`) — throttled (`HTTP 429`).
3. `mcp_courtlistener_search` (`type="r"`, `court="scotus"`, `case_name="Spicher"`, `num_results=10`) — returned 0 results (`query_id: 7505f0b4`).
4. `mcp_courtlistener_search` (`type="o"`, `court="ca4"`, `case_name="Spicher"`, `num_results=10`) — throttled (`HTTP 429`).

## Web Searches

- None performed.
