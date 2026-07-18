# Retrieval

## Corpus queries

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 5`
  - The command produced no result rows or transfer-statistics line before the corpus service attempt ended.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --limit 5`
  - No `ranged corpus reads` line was produced. Error: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`.

## CourtListener MCP

- Opinions search by neutral citation `2025-Ohio-1982`: throttled (HTTP 429; initial retry-after estimate 20 seconds).
- Opinions search for `uncodified law due process notice publication`: throttled (HTTP 429; initial retry-after estimate 20 seconds).
- Opinions search for `retroactive statute limitations reasonable time due process notice session law`: throttled (HTTP 429; initial retry-after estimate 20 seconds).
- After a bounded wait, opinions search for `"uncodified" "due process" publication law notice`: completed with zero results.
- Second opinions search by neutral citation `2025-Ohio-1982`: throttled (HTTP 429; retry-after estimate 48 seconds).
- Opinions search for `"session law" "due process" notice statute`: throttled (HTTP 429; retry-after estimate 48 seconds).

No further retry was made. No web search was used.

## Base-rate context

- `metrics/statpack.md`: modern discretionary-cert disposition, originating-court, relist, CVSG, and per-Term tables.
- `metrics/statpack.json`: 2025-Term paid-petition class rates.
