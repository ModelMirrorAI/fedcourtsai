# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `q=""2255(f)(1)" "co-defendant" certiorari "Clay v. United States""`, `num_results=10`, `fields=["caseName", "court", "dateFiled", "citation", "snippet"]`) — Checked federal case law addressing § 2255(f)(1) finality when a co-defendant files a certiorari petition under *Clay v. United States*.
