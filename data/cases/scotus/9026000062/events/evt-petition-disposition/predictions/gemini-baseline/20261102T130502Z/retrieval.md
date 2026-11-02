# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --judge Tymkovich --limit 10`
   - Stderr: `ranged corpus reads: 664 GET(s), 174063616 byte(s)`
   - Result: No matching rows returned (as noted in the prompt, `--judge` matches historical bulk-ingested SCOTUS rows rather than originating circuit judges).

2. `uv run fedcourts query --court scotus --citation "262 U.S. 649" --limit 10`
   - Stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Note: `note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all, and the column holds a case's OWN parallel cites (not a cases-citing-this-authority graph) — the filter is served off those rows alone, so an empty result here is far likelier a column that was never filled than a case that does not exist.`
   - Result: No matching rows returned.

## CourtListener MCP & Web Search

- None attempted beyond the provisioned inputs.
