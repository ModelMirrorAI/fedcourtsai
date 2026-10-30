# Retrieval Log

## 1. `fedcourts` Corpus Queries

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 34 GET(s), 8716288 byte(s)`
   - Result: Returned 10 recent OT2026/2020s granted SCOTUS cases for corpus schema and trajectory context.
2. `uv run fedcourts query --court scotus --docket-number 24-421`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned the prior certiorari petition in this exact prosecution (`scotus/69578654`, *Cynthia Davis, Warden v. David M. Smith*, No. 24-421, filed 2024-10-15, distributed 3 times, cert denied 2025-01-27).
3. `uv run fedcourts query --court scotus --citation "145 S. Ct. 93"`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Empty result (with CLI note that only 200 SCOTUS rows carry reporter citations).
4. `uv run fedcourts query --court ca6 --judge Thapar --limit 5`
   - Stderr: `ranged corpus reads: 85 GET(s), 22282240 byte(s)`
   - Result: Empty result for that filter combination.
5. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Stderr: `ranged corpus reads: 32 GET(s), 8192000 byte(s)`
   - Result: Returned 10 recent SCOTUS GVR dispositions for comparison.

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="ca6", case_name="Smith v. Davis", fields=["caseName", "dateFiled", "docketNumber", "citation", "judge", "cluster_id", "opinions"])`
   - Result: Failed with HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 5649 seconds.`). All lower-court opinions in *Smith v. Davis* were read directly from the provisioned `record/documents/appendix.txt`.

## 3. Web Searches

- None.
