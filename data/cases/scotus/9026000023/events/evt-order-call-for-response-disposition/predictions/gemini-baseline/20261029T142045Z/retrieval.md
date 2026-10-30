# Retrieval Log

## 1. Corpus Priors (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --decided-before 2026 --era 2020s --limit 10`
   - Stderr: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned 10 resolved SCOTUS priors from the 2020s era (sal-v4 scored cert petitions with their salience scores, originating courts, distribution counts, and dispositions).
2. `uv run fedcourts query --court scotus --citation "571 U.S. 69" --decided-before 2026`
   - Stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Note: `note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...` (0 rows returned due to sparse citation column coverage).
3. `uv run fedcourts query --court scotus --disposition granted --decided-before 2026-08-13 --limit 10`
   - Stderr: `ranged corpus reads: 43 GET(s), 11272192 byte(s)`
   - Note: `note: replay cutoff 2026-08-13 (from --decided-before) — priors that had not resolved by then are excluded, on top of any --decided-before Term`
   - Result: Returned 10 granted SCOTUS cert petitions resolved prior to `2026-08-13` with their distribution counts, CVSG dates, and salience scores.

## 2. CourtListener MCP Server Calls

1. `mcp_courtlistener_search(type="o", case_name="Harper v. Public Service Commission", fields=["caseName", "citation", "court", "dateFiled", "snippet"], num_results=3)`
   - Result: Error — `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 820 seconds.'}`
   - Fallback: Degraded gracefully per prompt instructions; relied on the provisioned `petition.txt` (including Appendices A–D) and `metrics/statpack.md`.

## 3. Web Searches

None attempted.
