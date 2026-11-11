# Retrieval Log (`scotus/9026000512`)

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer stderr: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS resolved rows (including recent OT2025/OT2026 denials and GVRs) for general context on current-Term conference dispositions and distribution counts.

2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - Transfer stderr: `ranged corpus reads: 24 GET(s), 6291456 byte(s)`
   - Result: Returned 5 recent 2020s SCOTUS granted petitions and substantive applications for comparison of distribution counts and salience characteristics on granted dockets.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Adel v. Hannah"`, `num_results=5`, `fields=["caseName", "citation", "court", "dateFiled", "docketNumber"]`)
   - Result: Confirmed the citation and date of the Arizona Supreme Court decision relied upon by the Arizona Court of Appeals below: *State ex rel. Adel v. Hon. Hannah Jr. / Ashley Buckman*, 249 Ariz. 537, 472 P.3d 1100 (Ariz. Sept. 25, 2020) (No. CV-19-0280-SA).
