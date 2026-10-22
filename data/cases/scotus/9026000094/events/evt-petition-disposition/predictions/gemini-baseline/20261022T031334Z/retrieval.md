# Retrieval Log

## Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000094" --event "evt-petition-disposition" --role predictor`
   - Resolved case, corpus, and event paths.
2. `uv run fedcourts query "Heck v. Humphrey" --court scotus --limit 10`
   - Returned CLI usage error (no free-text positional argument).
3. `uv run fedcourts query "party presentation" --court scotus --limit 10`
   - Returned CLI usage error (no free-text positional argument).
4. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
6. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 10`
   - `ranged corpus reads: 772 GET(s), 202375168 byte(s)`

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="ca9"`, `case_name="King v. Villegas"`)
   - Verified the panel opinion (`2025-10-20`) and the en banc vacatur order (`2026-04-03`) in Ninth Circuit Docket No. 23-1713.
2. `mcp_courtlistener_search` (`type="r"`, `docket_number="23-1713"`)
   - Located the Ninth Circuit RECAP docket for *King v. Villegas, et al.* (`23-1713`).
3. `mcp_courtlistener_call_endpoint` (`endpoint_id="dockets"`, `query={"court": "ca9", "docket_number": "23-1713", "fields": ["id", "case_name", "date_filed", "date_terminated"]}`)
   - Retrieved docket ID `71699439` and confirmed `date_terminated: null` (still pending en banc).
4. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 71699439, "fields": ["id", "entry_number", "date_filed", "description"], "order_by": "-date_filed"}`, `num_results=30`)
   - Confirmed that *King v. Villegas* was argued and submitted en banc on June 2, 2026 (Entry 88) and no en banc opinion had issued as of the prediction date.
