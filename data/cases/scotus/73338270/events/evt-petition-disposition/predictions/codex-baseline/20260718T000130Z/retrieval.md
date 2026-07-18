# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- Consulted `metrics/statpack.json` for the Term 2025 paid-petition grant rate (0.0536499560).

## Corpus lookups

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
  - Returned five recent granted SCOTUS priors. They were used only to inspect broad distribution-count and originating-court context; none was substantively treated as a close analogue.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - `ranged corpus reads: 201 GET(s), 52559872 byte(s)`
  - Returned five recent denied SCOTUS priors. They confirmed that three distributions is not uniquely grant-side; none was substantively treated as a close analogue.

## CourtListener MCP lookups

All searches were restricted to Ninth Circuit opinions filed before July 18, 2026. Each returned HTTP 429 without results; no direct REST fallback was used.

- Opinion search for `Boysen v. PeaceHealth` in the Ninth Circuit: HTTP 429, expected availability in 1 second.
- Opinion search for `Curtis v. Inslee` in the Ninth Circuit: HTTP 429, expected availability in 2 seconds.
- Opinion search for `Health Freedom Defense Fund v. Carvalho` in the Ninth Circuit: HTTP 429, expected availability in 1 second.
- One later retry of the `Curtis v. Inslee` opinion search: HTTP 429, expected availability in 8 seconds.

No web searches were used.
