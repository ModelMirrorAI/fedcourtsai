# Retrieval Log

- Read `metrics/statpack.md` for base rates (did not use a `fedcourts` tool because it requires a pulled corpus).
- Used CourtListener MCP server tool `mcp_courtlistener_search` with query `Louisiana v. Callais` and type `o` to verify the timing of the *Louisiana v. Callais* decision (decided April 29, 2026).
- `fedcourts query` was attempted (`uv run fedcourts query --court scotus --topic "Voting" --limit 5`) but failed because the local corpus service was unreachable (`corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running?`). No priors were retrieved.