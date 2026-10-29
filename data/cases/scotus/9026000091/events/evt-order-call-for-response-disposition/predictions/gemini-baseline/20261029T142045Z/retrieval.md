# Retrieval Log

## 1. Corpus CLI Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "532 U.S. 598" --decided-before "2026-09-10" --limit 5`
   - Stderr transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (sparse `citations` column coverage note printed).

2. `uv run fedcourts query --court scotus --disposition granted --decided-before "2026-09-10" --limit 10`
   - Stderr transfer line: `ranged corpus reads: 55 GET(s), 14417920 byte(s)`
   - Result: Returned 10 recently resolved/granted SCOTUS priors before `2026-09-10` for baseline context.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", citation="648 F.3d 946", filed_before="2026-09-10", fields=["caseName", "citation", "dateFiled", "court"])`
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 13889 seconds.'}`.

2. `mcp_courtlistener_search(type="o", case_name="Brown v. Baeke", filed_before="2026-09-10", fields=["caseName", "citation", "dateFiled", "court"])`
   - Result: Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 13888 seconds.'}`.

## 3. Web Searches

- None attempted.
