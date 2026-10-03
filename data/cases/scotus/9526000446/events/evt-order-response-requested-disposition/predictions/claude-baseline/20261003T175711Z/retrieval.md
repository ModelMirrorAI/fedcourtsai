# Retrieval log

Beyond the provisioned inputs (`event.yaml`, `record/context.json`,
`record/snapshots/2026-10-03.json`, `record/documents/application.txt`,
`record/documents/documents.json`) and the committed `metrics/statpack.md`
(interim-docket section) and `docs/salience.md` (interim section):

## Corpus

1. `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 25`
   stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   Returned 25 resolved 2020s SCOTUS rows, mostly 26A-series time-extension
   grants plus a few denials (26A370, 26A434, 26A437, 26A447) and two cert
   dockets; no ask filter exists, so it served as texture only.

## CourtListener MCP

2. `search` type=d, court=scotus, q="Wagner v. United States", filed_after=2026-09-01 → 0 results.
3. `search` type=d, court=ca6, docket_number=26-1294 → 1 result: *United States v. Kyle Wagner*,
   filed 2026-03-27, CourtListener docket 73117360.
4. `call_endpoint` docket-entries, docket=73117360 → HTTP 429 (rate limit, 300/hour).
5. `search` type=o, court=ca6, q="Wagner" "Bail Reform Act" detention "de novo" → HTTP 429.
6. `call_endpoint` dockets, court=scotus, docket_number=26-391 → HTTP 429.

No web searches. Nothing retrieved concerned this application's disposition.
