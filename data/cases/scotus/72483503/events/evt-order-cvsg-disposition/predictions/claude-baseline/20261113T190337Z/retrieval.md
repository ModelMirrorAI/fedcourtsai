# Retrieval log

- Read `metrics/statpack.md`: "Cert petitions by CVSG status (paid scored segment)", "by salience band", and "Segment base rate by salience band (sal-v8)".
- `uv run fedcourts query --help` (usage only).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — returned only the usage/help text (the flags as given were not accepted); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — 5 rows of recent grants (none topically related). stderr: `ranged corpus reads: 33 GET(s), 8585216 byte(s)`.
- No CourtListener MCP calls. No web searches. The Court's live docket page was not consulted.
