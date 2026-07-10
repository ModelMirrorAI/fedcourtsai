# Retrieval Log

Consulted committed base-rate context:

- `metrics/statpack.md`
- `metrics/statpack.json`

Attempted corpus lookup:

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --limit 8 --corpus-backend ranged`
- Result: failed before returning priors because the ranged backend could not resolve the remote host (`gaierror: [Errno -2] Name or service not known`). No `ranged corpus reads: ...` line was printed.

No CourtListener MCP lookups.

No web searches.
