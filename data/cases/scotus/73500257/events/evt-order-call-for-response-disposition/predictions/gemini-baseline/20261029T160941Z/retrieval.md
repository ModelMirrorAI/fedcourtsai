# Retrieval Log

## 1. Corpus Lookups (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number "25-1355" --limit 5`
   - Transfer: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Result: Returned the corpus row for `scotus/73500257` (*City of North Las Vegas, Nevada, et al. v. Genoa Jones, et al.*).
2. `uv run fedcourts query --court scotus --disposition gvr --limit 5`
   - Transfer: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Result: Returned 5 recent SCOTUS GVR priors (`scotus/73317900`, `scotus/73500268`, `scotus/73500579`, `scotus/9026000139`, `scotus/9026005216`).
3. `uv run fedcourts query --court ca9 --judge "Mendoza" --limit 5`
   - Transfer: `ranged corpus reads: 134 GET(s), 35127296 byte(s)`
   - Result: Returned 0 rows (circuit judge lists are withheld on the circuit slice).
4. `uv run fedcourts query --court scotus --citation "571 U.S. 3" -- citation "595 U.S. 1" --limit 5`
   - Result: CLI usage error (Exit Code 2: unexpected extra arguments due to space after `--`).
5. `uv run fedcourts query --court scotus --disposition summary-reversal --limit 10`
   - Transfer: `ranged corpus reads: 900 GET(s), 235536384 byte(s)`
   - Result: Returned 0 rows.
6. `uv run fedcourts query --court scotus --citation "146 S. Ct. 926" --limit 5`
   - Transfer: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Result: Returned 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all`).
7. `uv run fedcourts query --court scotus --citation "571 U.S. 3" --citation "595 U.S. 1" --limit 5`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", citation="146 S. Ct. 926", fields=["caseName", "dateFiled", "citation", "court", "cluster_id", "opinions"])`
   - Result: Error HTTP 429 (`Rate limit exceeded: 1400/day`).
2. `mcp_courtlistener_search(type="o", case_name="Jones v. City of North Las Vegas", fields=["caseName", "dateFiled", "citation", "court", "cluster_id", "opinions"])`
   - Result: Error HTTP 429 (`Rate limit exceeded: 1400/day`).
3. `mcp_courtlistener_search(type="o", case_name="Newman v. Underhill", fields=["caseName", "dateFiled", "citation", "court", "cluster_id", "opinions"])`
   - Result: Error HTTP 429 (`Rate limit exceeded: 1400/day`).
4. `mcp_courtlistener_extract_citations(text="Zorn v. Linton, 146 S. Ct. 926 (2026); Rivas-Villegas v. Cortesluna, 595 U.S. 1 (2021); City of Tahlequah v. Bond, 595 U.S. 9 (2021); Stanton v. Sims, 571 U.S. 3 (2013); Lange v. California, 594 U.S. 295 (2021); Kisela v. Hughes, 584 U.S. 100 (2018); District of Columbia v. Wesby, 583 U.S. 48 (2018).")`
   - Result: Extracted and resolved 7 citations locally via eyecite.

## 3. Web Searches

- None.
