# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3` — failed: "Unknown era 'modern'" (usage error; no rows, no ranged-reads line).
- `uv run fedcourts query --court scotus --docket-number 19-764` — `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned the 2019 Sokolow v. PLO petition row (the 2020 GVR in light of the PSJVTA).
- `uv run fedcourts query --court scotus --docket-number 24-151` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned United States v. PLO (Fuld companion) row.
- Read `metrics/statpack.md` (sal-v6 segment base rate by salience band table).
- No CourtListener MCP or web searches.
