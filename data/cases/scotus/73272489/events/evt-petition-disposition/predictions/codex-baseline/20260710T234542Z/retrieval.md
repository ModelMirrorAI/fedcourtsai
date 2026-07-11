# Retrieval

- Consulted `metrics/statpack.md`. Its corpus roll-up reports a 1.4% grant share among 296 resolved SCOTUS records, but the labels are dominated by `other` and `dismissed`; the prompt-described "Modern discretionary-cert petitions by disposition" section is absent. I treated this only as directional evidence that grants are rare.
- Attempted `uv run fedcourts query --court scotus --disposition granted --limit 5 --corpus-backend ranged`. The lookup failed because the remote corpus host could not be resolved. No `ranged corpus reads: ...` line was emitted because the connection failed before a successful GET.
- Attempted CourtListener MCP `search` for Supreme Court opinions matching `"not a court of error correction" certiorari` (court `scotus`, five results). The server returned `REDIS_URL is not set; cannot access session store.` No results were consulted.
- No web searches were used.
