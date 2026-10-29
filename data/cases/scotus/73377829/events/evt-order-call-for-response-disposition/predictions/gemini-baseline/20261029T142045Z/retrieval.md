# Retrieval Log (`scotus/73377829` — `evt-order-call-for-response-disposition`)

## 1. Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer line: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Returned 5 recent granted SCOTUS rows (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`).
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 recent denied SCOTUS rows (`scotus/9526000499`, `scotus/9526000535`, `scotus/9526000532`, `scotus/9526000555`, `scotus/9526000556`).
3. `uv run fedcourts query --judge "Ronald Lee Gilman" --limit 5`
   - Transfer line: `ranged corpus reads: 1381 GET(s), 362020864 byte(s)`
   - Returned 0 rows (judge filter on circuit/SCOTUS slice had no matching resolved priors).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", citation="32 F.4th 311", fields=["id", "caseName", "dateFiled", "court", "citation"])`
   - Result: Error HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 1713 seconds.`).
2. `mcp_courtlistener_search(type="o", citation="398 F.3d 156", fields=["id", "caseName", "dateFiled", "court", "citation"])`
   - Result: Error HTTP 429 (`Rate limit exceeded: 1400/day. Expected available in 1713 seconds.`).
3. `mcp_courtlistener_extract_citations(text="Strickland v. United States, 32 F.4th 311 (4th Cir. 2022); Strickland v. Moritz, 149 F.4th 378 (4th Cir. 2025); Strickland v. United States, 744 F. Supp. 3d 477 (W.D.N.C. 2024); Dotson v. Griesa, 398 F.3d 156 (2d Cir. 2005); In re Golinski, 587 F.3d 956 (9th Cir. 2009); In re Levenson, 587 F.3d 925 (9th Cir. 2009); Davis v. Passman, 442 U.S. 228 (1979); Spreen v. Brey, 961 F.2d 109 (7th Cir. 1992).")`
   - Result: Extracted and resolved all 8 unique case citations locally via eyecite.

## 3. Web Searches

- None attempted.
