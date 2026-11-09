# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number "26-355" --decided-before 0`
   - Transfer line: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned 1 row (`scotus/9026000355`, *Julio del Rio, et al. v. CrowdStrike, Incorporated, et al.*, open, `distribution_count: 1`, `salience_score: 0.0337`).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 0 --limit 10`
   - Transfer line: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Returned 10 recent granted SCOTUS priors from the 2020s era for baseline context.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", q='"Airline Deregulation Act" "CrowdStrike"')`
   - Returned 0 results (`count: 0`).

2. `mcp_courtlistener_search(type="o", court="scotus", q='"41713" "service of an air carrier"')`
   - Returned 4 SCOTUS opinions (*Northwest Airlines, Inc. v. Duncan*, 531 U.S. 1058 (2000); *Northwest, Inc. v. Ginsberg*, 572 U.S. 273 (2014); *Dan's City Used Cars, Inc. v. Pelkey*, 569 U.S. 251 (2013); *American Airlines, Inc. v. Wolens*, 513 U.S. 219 (1995)).
