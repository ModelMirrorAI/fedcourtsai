# Retrieval
- `uv run fedcourts query --court scotus --docket-number 26A203 --include-applications`: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`. Returned the companion stay application row (substantive, 7 amicus entries). Confirms the stay docket exists; it was used only for context.
- `uv run fedcourts query --court scotus --docket-number 25-845`: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned Abbott v. LULAC, the summary-reversal precedent the petition cites (an appeal, not cert).
- Two earlier `query --docket-number` attempts without `--court` were refused with a usage error and returned nothing.
- `metrics/statpack.md`: the salience band table (sal-v7) and the interim applicant-class table.
- No CourtListener MCP or web searches.
