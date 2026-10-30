# Retrieval

- `uv run fedcourts query --court scotus --include-applications --decided-before 2017 --limit 5`
  - `ranged corpus reads: 274 GET(s), 71827456 byte(s)`
  - It returned recent OT2016 applications, mostly extensions plus one denied substantive application (Fisch v. United States). Not informative; I did not use them.
- `uv run fedcourts paths …` (path resolution only).
- Read `metrics/statpack.md` (interim docket section) for the base rate.
- No CourtListener MCP or web calls. I deliberately avoided them because this 2017 docket is almost certainly already decided (see flags.json).
