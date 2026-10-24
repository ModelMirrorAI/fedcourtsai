# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "508 U.S. 36"`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Stinson v. United States"`, `num_results=5`, `fields=["caseName", "citation", "dateFiled", "cluster_id"]`)
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Kisor v. Wilkie"`, `num_results=5`, `fields=["caseName", "citation", "dateFiled", "cluster_id"]`)

## Web Searches

- None.
