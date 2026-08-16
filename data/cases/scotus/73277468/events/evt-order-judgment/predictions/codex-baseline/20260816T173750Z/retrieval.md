# Retrieval

- Consulted `metrics/statpack.md`, "The merits docket (granted cases)," for the strictly prior grant-Term baseline: 359 disturbed among 515 parsed judgments for Terms 2017-2024.
- CourtListener MCP opinion search: `type=o`, query `"affirmative defense" "Rule 8(c)" prejudice waiver summary judgment`, court `scotus`, filed before `2026-03-30`, limit 10. The server returned HTTP 429 (daily rate limit exceeded); no result informed the forecast.
- `uv run fedcourts query --court scotus --citation '547 U.S. 198' --citation '566 U.S. 463' --citation '371 U.S. 178' --citation '540 U.S. 443' --full --limit 4`. The service returned no rows and printed no `ranged corpus reads` line before the invocation ended.
- `uv run fedcourts query --court scotus --citation '547 U.S. 198' --limit 3`. The service returned no rows and printed no `ranged corpus reads` line before stalling; the invocation was interrupted.
- No web searches.
