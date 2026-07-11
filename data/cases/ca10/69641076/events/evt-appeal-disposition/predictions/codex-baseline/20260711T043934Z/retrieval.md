# Retrieval

- Consulted `metrics/statpack.md`, especially the overall and Tenth Circuit disposition base rates.
- Attempted `uv run fedcourts query --court ca10 --era 2010s --limit 10 --corpus-backend ranged`. The lookup failed before returning results because the configured remote hostname could not be resolved (`EndpointConnectionError`). It emitted no `ranged corpus reads: ...` line.
- No CourtListener MCP or web lookup was made. In particular, I did not query this case or follow the opinion-cluster link in the provisioned snapshot.
