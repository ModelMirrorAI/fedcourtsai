# Retrieval log

- `uv run fedcourts query --court scotus --disposition denied --era modern --limit 5`: usage error (the flag was rejected, and the help text was printed). No reads.
- `uv run fedcourts query --court scotus --disposition denied --limit 5`
  - stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
  - Returned recent denied SCOTUS application rows (e.g., Silva v. Blanche, Walker v. Purdue). Generic and not informative here.
- Read `metrics/statpack.md`, the "Segment base rate by salience band (sal-v6)" table (baseline reached rates of about 4–6% per Term).
- CourtListener MCP `search` (type o, court ca11, case_name "Shaikh v. Fox News"), twice with different fields. Found the CA11 opinion of 2026-06-04, No. 25-12004, published, id 11337751.
- CourtListener MCP `read_document` (opinion 11337751, chunks 0–1): the opinion text summarized in reasoning.md.
