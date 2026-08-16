# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `event.yaml`) and the committed `metrics/statpack.md`
("The interim docket (applications)" section — the base-rate anchor):

## Corpus queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --include-applications --era modern --limit 8`
   — returned no rows.
   `ranged corpus reads: 743 GET(s), 194772992 byte(s)`
2. `uv run fedcourts query --court scotus --include-applications --limit 8`
   — returned 8 rows, mostly recent time-extension applications plus one
   substantive application (Hines v. Tennessee); no closely comparable
   government-applicant stay prior surfaced.
   `ranged corpus reads: 1 GET(s), 262144 byte(s)`

## CourtListener MCP

1. `search` (opinions, court=ca1, docket_number=26-1774) — **failed**: HTTP
   429, daily rate limit exhausted ("Rate limit exceeded: 1400/day"). No
   further MCP calls attempted; degraded to provisioned inputs and the
   statpack per the prompt's degradation rule.

No web searches.
