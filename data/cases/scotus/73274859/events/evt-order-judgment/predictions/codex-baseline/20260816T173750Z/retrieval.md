# Retrieval

- Consulted the committed `metrics/statpack.md`, “The merits docket (granted cases),” and pooled the available strictly prior grant Terms 2017–2024: 359 disturbed / 515 parsed = 69.7%.
- CourtListener MCP search: opinions query for `Hencely v. Fluor federal common law uniquely federal interests`, restricted to SCOTUS opinions filed after 2025-01-01. The server returned HTTP 429 (`Rate limit exceeded`) and no results were used.
- Corpus query: `uv run fedcourts query --court scotus --citation '564 U.S. 410' --citation '479 U.S. 481' --citation '490 U.S. 605' --citation '420 U.S. 469' --citation '590 U.S. 1' --limit 5 --corpus-backend service`. It returned no rows and no `ranged corpus reads` line.
