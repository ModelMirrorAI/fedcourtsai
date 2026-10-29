# Retrieval Log

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --term 2025 --disposition granted --limit 20`
   - Result: CLI usage error (`No such option: --term (Possible options: --era)`).
2. `uv run fedcourts query --court ca2 --case-name "Kwok" --limit 10`
   - Result: CLI usage error (`No such option: --case-name (Possible options: --docket-number)`).
3. `uv run fedcourts query --court scotus --qp-topic bankruptcy --limit 20`
   - Result: CLI usage error (`No such option: --qp-topic (Possible options: --topic)`).
4. `uv run fedcourts query --court scotus --docket-number 26-194 --include-open --full`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned 1 row (`scotus/9026000194`, *Mei Guo, et al. v. Luc A. Despins, Chapter 11 Trustee*, open, distributed 2026-09-28, counsel including Jeffrey Alan Lamken for amicus Official Committee of Unsecured Creditors in the Chapter 11 Case of Vanderbilt Minerals, LLC).
5. `uv run fedcourts query --court scotus --disposition granted --limit 15`
   - Transfer: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Result: Returned 15 recent granted SCOTUS rows from OT2025/OT2026 for comparison.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(case_name="Mei Guo v. Despins", type="o")`
   - Result: Failed with `HTTP 429: Request was throttled. Rate limit exceeded: 1400/day. Expected available in 13557 seconds.`
2. `mcp_courtlistener_search(q=""544(a)" "alter ego" "general claim"", type="o")`
   - Result: Failed with `HTTP 429: Request was throttled. Rate limit exceeded: 1400/day. Expected available in 13557 seconds.`
