# Retrieval log

Mode: `forward` (context.json). No search was made for, and none surfaced, any disposition or post-grant history of this case.

## Corpus (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "581 U.S. 214" --limit 3`
   `ranged corpus reads: 10 GET(s), 2621440 byte(s)` — no rows; `note:` line reported only 200 SCOTUS rows carry any reporter citation (coverage gap, not absence).
2. `uv run fedcourts query --court scotus --citation "490 U.S. 581" --limit 3`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` — no rows; same `note:` line.
3. An initial `fedcourts query --text ...` attempt was refused (the command takes no free-text argument); no corpus read occurred.

Base rates: the committed `metrics/statpack.md`, "The merits docket (granted cases)" section (pooled Terms 2017-2025: 377 disturbed / 540 parsed).

## CourtListener MCP

1. `search` (type `o`, court `nd`, filed after 2026-01-01, q "Marschner Howell disability retired pay indemnify") — 1 result: Marschner v. Marschner, 2026 ND 66, cluster 10803887, opinion 11270617.
2. `search` (type `o`, court `scotus`, filed 2017, q "Howell v. Howell military retirement disability indemnify preempted") — 2 results; used cluster 4391111, opinion 4168364.
3. `read_document` opinion 11270617 (full text, ~25.6k chars) — the North Dakota Supreme Court opinion below and the Chief Justice's concurrence.
4. `read_document` opinion 4168364, chunks 2-3 of 5 (chunk size 8000) — Howell v. Howell, Part II of the opinion of the Court, the disposition, Gorsuch's non-participation, and the opening of Thomas's partial concurrence.
5. `search` (type `d`, court `scotus`, q "Tronsrue") — 0 results (the Tronsrue cert docket, No. 25-500, is not indexed; its denial is taken from the brief in opposition).

Five MCP calls and three corpus command invocations in total. No web searches.
