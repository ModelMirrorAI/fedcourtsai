# Retrieval

- Consulted the committed aggregate base-rate report `metrics/statpack.md`, including the modern discretionary-cert, originating-circuit, relist, CVSG, and Term 2025 sections. This is a local committed artifact and produced no ranged-read transfer line.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic "Anderson-Burdick" --limit 5`. The lookup failed because the ranged corpus host could not be resolved and returned no priors. It failed before a transfer completed, so it printed no `ranged corpus reads: ...` line.
- No CourtListener MCP lookup or web search was performed.
