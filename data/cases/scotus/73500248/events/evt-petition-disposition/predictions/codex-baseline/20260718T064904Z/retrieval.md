# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted the 2025 Term paid-fee-class detail in `metrics/statpack.json`.

## Corpus lookups

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '583 U.S. 220' --citation '477 U.S. 561' --limit 5`
  - Returned no rows and printed no ranged-read statistics line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5 --corpus-backend service`
  - `ranged corpus reads: 133 GET(s), 34865152 byte(s)`
  - Returned five contemporary grant-side priors. They were used only as general context for the importance of repeated distributions and were not treated as factually similar cases.

## CourtListener MCP

- Attempted an opinions search for `"42 U.S.C. § 1997e(d)(2)" "150 percent" attorney fees`, requesting compact case metadata and ten results.
  - The server returned HTTP 429: daily rate limit exceeded, with an expected availability window of 267 seconds. I did not retry or use any search results.

No web searches were used.
