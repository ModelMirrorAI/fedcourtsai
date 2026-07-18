# Retrieval

- Consulted `metrics/statpack.md`, especially the modern discretionary-cert, relist, CVSG, and 2025 Term sections, and `metrics/statpack.json` for the 2025 Term paid-petition estimate.
- Attempted a CourtListener MCP opinion search for `Kamani v. Stone`, limited to opinions filed before January 8, 2026. The service returned HTTP 429 (daily rate limit exceeded); no result content informed the prediction.
- Attempted `fedcourts query --court scotus --era 2020s --limit 8`. The corpus query service returned no results before timing out; no `ranged corpus reads` line was printed.
- Attempted `fedcourts query --court scotus --limit 5`. The command reported that the local corpus service was unreachable and timed out; no `ranged corpus reads` line was printed.
- No web search was used.
