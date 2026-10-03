# Retrieval log

Beyond the provisioned inputs (`event.yaml`, `record/context.json`, the
`2026-09-28.json` snapshot, `record/documents/documents.json` and the empty
`application.txt`) and the committed `metrics/statpack.md`:

## Corpus (`fedcourts query`)

- `uv run fedcourts query --court scotus --include-applications --limit 15`
  - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  - Returned the most recent SCOTUS application rows: eleven time-extension
    grants (26A390, 26A409, 26A429–26A445), two resolved substantive
    applications (26A370 and 26A447, both `denied`), and two cert dockets.
    Rows carry no caption or ask, so they served only as a shape check on the
    current Term's substantive stream.

## CourtListener MCP

1. `search` (type `o`, q `Holloway Polk`, courts `tex`/`texapp`, filed after
   2024-01-01) — 2 unrelated results.
2. `search` (type `d`, q `Holloway Polk`, Texas federal courts + `ca5`) — 2
   unrelated results.
3. `search` (type `o`, docket_number `26-0569`, court `tex`) — 0 results; the
   Texas Supreme Court matter is not in the opinions index.
4. `search` (type `d`, docket_number `26A449`, court `scotus`) — 0 results;
   this application is not in RECAP.
5. `search` (type `o`, q `"Holloway" "Polk"`, `tex`/`texapp`) — 3 unrelated
   results.
6. `search` (type `r`, q `"Elisha Holloway"`) — 8 results, including
   *Holloway v. Polk*, N.D. Tex. 4:25-cv-01128 (filed 2025-10-10, nature of
   suit Civil Rights: Other Civil Rights, docket_id 71611942, not terminated),
   and a series of pro se N.D. Tex. and CA5 matters by the same applicant
   (*Holloway v. Revelstoke Venture*, *Holloway v. Equifax*, *Holloway v.
   RentGrow*).
7. `search` (type `o`, q `"Elisha Holloway" OR "Holloway v. Polk"`, filed
   after 2022-01-01) — 5 Texas court of appeals opinions naming the applicant:
   two in *Holloway v. Revelstoke Venture* (Fort Worth, 2024), *In re Elisha
   Holloway v. State of Texas* (Fort Worth, 2024, a mandamus), *Holloway v.
   BT1, LLC* (Waco, 2025), and *Holloway v. The Julian at South Pointe* (Waco,
   2026-04-23, 10-26-00060-CV).
8. `search` (type `d`, party_name `Holloway`, `tex`/`texapp`, filed after
   2024-06-01) — 0 results.
9. `call_endpoint` (`docket-entries`, docket 71611942) — **HTTP 429**, rate
   limit exceeded (300/hour shared); not retried.
10. `get_endpoint_item` (`clusters`, 10847429) — **HTTP 429**; not retried.
11. `get_endpoint_item` (`dockets`, 71611942) — rejected for an invalid field
    name (`parties`); not retried once the throttle was evident.

No call sought this application's disposition, and none surfaced it.

## Web

None.
