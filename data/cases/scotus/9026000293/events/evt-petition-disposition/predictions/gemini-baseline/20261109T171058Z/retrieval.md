# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
   - Returned 10 recent OT 2026 SCOTUS GVR dispositions (`26-5123`, `25-1269`, `25-1367`, `25-7569`, `26-139`, `26-5216`, `25-901`, `25-918`, `25-7462`, `25-7532`).

2. `uv run fedcourts query --court scotus --docket-number 24-699`
   - Transfer line: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Returned `scotus/72317507`, *Exxon Mobil Corporation v. Corporación Cimex, S.A. (Cuba), et al.*, No. 24-699 (cert granted Oct. 3, 2025 after CVSG; merits decided June 23, 2026, reversed).

3. `uv run fedcourts query --court scotus --docket-number 26-292`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned companion vided docket `scotus/9026000292`, *Fiona Havlish, et al. v. The Taliban, et al.*, No. 26-292 (`distribution_count = 2`, `distributed_for_conference = 2026-11-13`, `salience_score = 0.1008`).

4. `uv run fedcourts query --court scotus --docket-number 26-294`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned companion vided docket `scotus/9026000294`, *James Owens, et al. v. The Taliban, et al.*, No. 26-294 (`distribution_count = 2`, `distributed_for_conference = 2026-11-13`, `salience_score = 0.1008`).

5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent OT 2026 SCOTUS granted cases for distribution-count and salience comparison.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="170 F.4th 100", fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "court_id", "opinions"])`
   - Result: `count: 0` (the Second Circuit en banc denial order at 170 F.4th 100 was not indexed under that citation in CourtListener).

2. `mcp_courtlistener_search(type="o", citation="146 S. Ct. 1909", fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "court_id", "opinions"])`
   - Result: `count: 2` (matched unrelated older cases containing `1909` and `146`; *Exxon Mobil Corp. v. Corporación CIMEX* was not indexed under `146 S. Ct. 1909` in CourtListener search).

3. `mcp_courtlistener_search(type="o", court="ca2", case_name="Havlish v. The Taliban", filed_after="2025-01-01", fields=["cluster_id", "caseName", "dateFiled", "citation", "opinions"])`
   - Result: `count: 0` (relied instead on the full Second Circuit panel opinion and dissent reproduced in Appendix A of `record/documents/petition.txt`).
