# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted the 2025 paid-petition detail in `metrics/statpack.json` (estimated grant rate 5.36%).

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation 'Florida v. Jardines' --limit 8`
- Result: failed before returning any priors because the runner could not resolve the ranged corpus remote host. No `ranged corpus reads: …` line was printed.

## CourtListener MCP

- Opinion search: `"knock and talk" Jardines "purpose to conduct a search"`, filed after March 26, 2013, 10 results. It returned 36 matches and surfaced the principal decisions discussed by the parties, including *People v. Frederick*, *United States v. White*, and *United States v. Walker*.
- SCOTUS opinion search: `"knock and talk" Jardines`, filed after March 26, 2013, 10 results. It returned *Florida v. Jardines* as the sole indexed result.

No web searches were used, and no lookup sought this case's disposition or subsequent history.
