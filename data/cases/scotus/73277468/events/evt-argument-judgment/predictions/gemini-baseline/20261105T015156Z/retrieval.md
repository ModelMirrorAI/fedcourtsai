# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "598 U.S. 729" --citation "540 U.S. 443" --limit 5`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: 0 rows returned (note on sparse `citations` column coverage).

2. `uv run fedcourts query --court scotus --docket-number 25-352`
   - Transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned corpus metadata row for `scotus/73277468` (*Jasmine Younge v. Fulton Judicial Circuit District Attorney's Office, Georgia*).

3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - Transfer line: `ranged corpus reads: 24 GET(s), 6291456 byte(s)`
   - Result: Returned 5 recent granted SCOTUS rows (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`).

## CourtListener MCP Lookups

- None attempted (all lower-court decisions, merits briefs, and the oral argument transcript were provisioned directly in `record/documents/`).

## Web Searches

- None attempted.
