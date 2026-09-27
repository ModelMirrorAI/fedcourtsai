# Retrieval log

Beyond the provisioned inputs (snapshot 2026-09-18.json, context.json, application.txt, event.yaml, the sibling event.yaml at events/evt-order-response-requested-disposition/, and metrics/statpack.md), I consulted:

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --include-applications --disposition granted`
   stderr: `ranged corpus reads: 7 GET(s), 1703936 byte(s)`
   Result: 20 rows, top-ranked substantive grants 26A308 (DHS v. League of Women Voters) and 26A388 (People Not Politicians v. Onder); the remainder time-extension grants.
2. `uv run fedcourts query --court scotus --include-applications --disposition denied`
   stderr: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   Result: 20 rows, mostly substantive denials of private and pro se applications (26A391, 26A363, 26A374, 26A380, 26A397, 26A325, 26A375, 26A358, 26A337, 26A332, 26A353, 26A305, 26A306, 26A296, 26A298).
3. `uv run fedcourts corpus-info` — raised an exception (no local blob; read-only connect failed). No vintage line obtained.

## CourtListener MCP

1. `search` type=d, court=scotus, docket_number=26A382 — 0 results.

## Web

1. WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/26a382.html` — Proceedings and Orders as of 2026-09-27: Sep 17 application submitted to Justice Sotomayor; Sep 23 response requested by Justice Sotomayor, due 4 p.m. Sep 28, 2026; Sep 25 amicus brief of The Becket Fund for Religious Liberty submitted. No disposition.
2. WebSearch "Strulovitch Bain Supreme Court stay application beis din seruv Sotomayor" — links to the Notre Dame Religious Liberty Clinic press release and the application PDF, plus unrelated pages. The tool's generated summary asserted a grant dated August 24, 2026, which predates the application and contradicts the docket page; disregarded and flagged.
