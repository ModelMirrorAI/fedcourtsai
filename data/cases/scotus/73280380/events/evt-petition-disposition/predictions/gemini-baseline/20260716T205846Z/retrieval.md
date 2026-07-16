- `uv run fedcourts query --court scotus --decided-before 2026-07-16 --era 2020s "Rule 11 sanctions" "1927" "election" "dissent from denial of rehearing en banc"` (failed)
- `uv run fedcourts query --court scotus --decided-before 2026-07-16 "Rule 11 sanctions attorneys" "send a message" "frivolous"` (failed)
- MCP CourtListener `search` query: `"Rule 11" AND ("sanction" OR "sanctions") AND "chill"`
- MCP CourtListener `search` query: `"Rule 11" AND "1927" AND "sanctions"`

Also consulted the provisioned `metrics/statpack.md` to review the baseline cert grant rates for the 9th Circuit and cases with zero relists.