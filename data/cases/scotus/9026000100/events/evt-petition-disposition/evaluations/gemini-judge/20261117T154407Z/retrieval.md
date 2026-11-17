# Evaluator Retrieval Log (`scotus/9026000100`, `evt-petition-disposition`, `gemini-judge`, `20261117T154407Z`)

## Prediction-Time Statpack Rebuilds (`fedcourts statpack-at`)
Reconstructed the statpack vintage in force at candidate run `20261025T012628Z` (`eb6830084a187953fd58b91cb3c9125fc6775a7b`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, landed `2026-10-19T08:07:55-04:00`, `alternative_sha: null`) for all three blinded candidates:
- `uv run fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`

## Corpus Queries (`fedcourts query`)
1. `uv run fedcourts query --court scotus --docket-number "24-427"` (verified *Ronald Hittle v. City of Stockton, California, et al.*, `scotus/69719675`, cert denied `2025-03-10`, `distribution_count: 5`, counsel and amici overlap):
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
2. `uv run fedcourts query --court scotus --docket-number "23-1039"` (verified *Marlean A. Ames v. Ohio Department of Youth Services*, `scotus/69676206`, cert granted `2024-10-04`, merits decided `2025-06-05`, vacated):
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`

## CourtListener MCP Lookups
1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Ames v. Ohio Department of Youth Services"`, `fields=["caseName", "dateFiled", "citation", "cluster_id", "opinions"]`, `num_results=3`):
   - Returned HTTP 429 rate-limit error (25/min limit); verified *Ames* lineup directly from the staged `brief-in-opposition.txt` (p. 17) and corpus row `scotus/69676206` instead.

## Web Searches
None.
