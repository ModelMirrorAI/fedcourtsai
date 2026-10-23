# Retrieval Log

## Corpus CLI Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73282277" --event "evt-order-judgment" --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query --court scotus --docket-number 25-166`
   - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Retrieved companion petition *Parada v. United States*, No. 25-166 (`scotus/73274854`, cert denied `2026-01-12`).
3. `uv run fedcourts query --court scotus --docket-number 24-7489`
   - `ranged corpus reads: 594 GET(s), 155713536 byte(s)`
   - Retrieved companion petition *Minor v. Florida*, No. 24-7489 (`scotus/72486976`).
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Sampled recent 2020s SCOTUS granted dockets.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="r"`, `case_name="Kian v. Florida"`) — failed with `HTTP 429: Rate limit exceeded: 300/hour`.
2. `mcp_courtlistener_search` (`type="o"`, `case_name="Khorrami v. Arizona"`) — failed with `HTTP 429: Rate limit exceeded: 300/hour`.
3. `mcp_courtlistener_search` (`type="o"`, `case_name="Cunningham v. Florida"`) — failed with `HTTP 429: Rate limit exceeded: 300/hour`.

## Web Searches (`google_web_search`)

1. `"Kian v. Florida" "25-6623" Supreme Court` — no results returned.
2. `"Kian v. Florida" OR "25-6623" "Williams v. Florida"` — no results returned.
