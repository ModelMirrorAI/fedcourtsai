# Retrieval Log

## Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73279966" --event "evt-brief-sg-disposition" --role predictor`
   - Resolved cell paths (`case_id: scotus/73279966`).
2. `uv run fedcourts query --court scotus --docket-number "26-71" --include-open`
   - `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Checked status of companion/related petition *The GEO Group, Inc. v. Ferguson* (formerly *Inslee*), No. 26-71, referenced in the Solicitor General's brief and Petitioner's reply brief.
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Checked recent granted SCOTUS petitions in the corpus.

## CourtListener MCP Lookups

None.

## Web Searches

None.
