# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Purpose: Inspect recent 2020s SCOTUS denied certiorari and application priors (`scotus/9526000416`, `scotus/9526000524`, `scotus/9526000530`, `scotus/9526000536`, `scotus/73265705`).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   - Purpose: Inspect recent 2020s SCOTUS granted certiorari priors (`scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`).

*(Note: Two initial exploratory invocations of `fedcourts query` with `--text` exited with usage help before running any corpus reads.)*

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="United States v. Maebane"`, `num_results=5`)
   - Purpose: Verify military appellate citation context referenced in the NMCCA opinion (`United States v. Maebane`, decided by NMCCA on 2022-06-07 and CAAF on 2025-09-18).
