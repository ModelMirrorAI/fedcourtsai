# Retrieval

- Read the committed `metrics/statpack.md`: the "Segment base rate by salience band (sal-v6)" table, federal column.
- `uv run fedcourts query --court scotus --docket-number 26-210`. Stderr: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`. It returned *Trump v. Thakur* (CA9 25-4249), filed 2026-08-19, distributed for the 2026-11-13 conference, distribution_count 1, undecided.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` was refused as a usage error ("Unknown era 'modern'"), so no data came back.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`. Stderr: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`. It returned recent grants, including several SG petitions (DOJ v. McNutt, DOGE Service, Blanche v. Ozurumba).
- I made no CourtListener MCP calls and no web searches.
