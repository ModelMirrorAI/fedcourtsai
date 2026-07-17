# Retrieval

## Committed base rates

Consulted `metrics/statpack.md` and the Term 2025 paid-fee detail in `metrics/statpack.json` for modern discretionary-cert, originating-circuit, relist, CVSG, Term, and fee-class base rates.

## Corpus query

Attempted:

`UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '565 U.S. 400' --citation '482 U.S. 691' --citation '576 U.S. 409' --limit 10`

The lookup failed because the configured corpus endpoint could not be resolved (`EndpointConnectionError`). It returned no priors and emitted no `ranged corpus reads: ...` line because the failure occurred before a ranged read completed.

No CourtListener MCP lookup or web search was available or used.
