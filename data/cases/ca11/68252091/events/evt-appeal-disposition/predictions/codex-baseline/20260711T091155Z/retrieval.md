# Retrieval

- Consulted `metrics/statpack.md`, especially the overall and Eleventh Circuit disposition base rates.
- Attempted `uv run fedcourts query --court ca11 --limit 10 --corpus-backend ranged`. The lookup failed with a name-resolution error before producing results; consequently, it printed no `ranged corpus reads: …` line.
- Attempted a CourtListener opinions search limited to the Eleventh Circuit for `mandamus "clear and indisputable" "adequate means"`. The MCP service reported that its session store was unavailable and supplied no results.

No search targeted this case's disposition or subsequent history.
