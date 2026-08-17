# Retrieval log

- CourtListener MCP opinion search: `\"meaningful benchmark\" ERISA prudence`, limited to SCOTUS and the Second, Sixth, Seventh, Eighth, Ninth, and Tenth Circuits. The server returned HTTP 429 (daily rate limit exceeded); no search results were used.
- Corpus lookup: `uv run fedcourts query --court scotus --citation '595 U.S. 170' --citation '573 U.S. 409' --limit 5 --full`. The lookup returned no rows and emitted no `ranged corpus reads` line before ending.
- Corpus lookup: `uv run fedcourts query --court scotus --citation '595 U.S. 170' --limit 5`. The lookup emitted no rows and no `ranged corpus reads` line, remained pending for about a minute, and was interrupted.
- Base-rate context: `metrics/statpack.md`, “The merits docket (granted cases),” using the 2017–2024 grant-Term rows in the ten-Term lookback window.
