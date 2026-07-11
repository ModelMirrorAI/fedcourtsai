# Retrieval

## Committed base-rate context

- Consulted `metrics/statpack.md`. It reports a 1.4% grant share among 296 resolved SCOTUS records, but contains no “Modern discretionary-cert petitions by disposition” section and no resolved observations for the 2025 Term or Second Circuit-origin SCOTUS petitions. I used it only as a broad rarity prior.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation 'Libretti v. United States, 516 U.S. 29' --citation 'Apprendi v. New Jersey, 530 U.S. 466' --citation 'Southern Union Co. v. United States, 567 U.S. 343' --era 2020s --limit 10 --corpus-backend ranged`
- Result: failed before any corpus data was returned because the remote host could not be resolved. No `ranged corpus reads: …` line was printed.

## CourtListener MCP lookup

- Searched opinions for `Libretti Apprendi criminal forfeiture jury`, limited to the Second, Third, Sixth, Seventh, Eighth, Ninth, and Tenth Circuits and filings after January 1, 2000.
- Result: failed with `REDIS_URL is not set; cannot access session store.` No search results were returned or used.

No web searches were performed.
