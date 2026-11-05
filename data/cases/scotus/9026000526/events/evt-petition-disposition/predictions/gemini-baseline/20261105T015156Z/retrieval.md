# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Returned 5 recent 2020s-era SCOTUS denied rows for general baseline context.

2. `uv run fedcourts query --court scotus --citation "601 U.S. 87" --citation "568 U.S. 313" --limit 5`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows with a `note:` that reporter citations are sparsely populated on corpus rows.

3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Stderr: `ranged corpus reads: 22 GET(s), 5767168 byte(s)`
   - Returned 5 recent 2020s-era SCOTUS granted rows (showing typical relist, amicus, and federal-petitioner profiles of granted cases).

4. `uv run fedcourts query --court scotus --docket-number "26A324"`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned the linked extension application `scotus/9526000324` (`26A324`, *Lane Douglas Mitchell v. Mississippi*), confirming it was a routine time-extension application granted on September 10, 2026.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Mississippi v. Mitchell", num_results=5, fields=["caseName", "court", "dateFiled", "docketNumber", "citation", "cluster_id", "opinions"])`
   - Returned 5 Mississippi appellate opinions involving other defendants named Mitchell; the full text of the Mississippi Court of Appeals en banc decision in *State of Mississippi v. Lane Mitchell*, No. 2023-KA-00771-COA (Miss. Ct. App. July 15, 2025), was already provisioned in full in `record/documents/petition.txt` (Appendix A, pp. 1a–44a).

2. `mcp_courtlistener_search(type="o", q=""McElrath v. Georgia" "Evans v. Michigan" acquittal", num_results=5, fields=["caseName", "court", "dateFiled", "docketNumber", "citation"])`
   - Returned 8 opinions citing both *McElrath v. Georgia*, 601 U.S. 87 (2024), and *Evans v. Michigan*, 568 U.S. 313 (2013), on Double Jeopardy acquittal finality.
