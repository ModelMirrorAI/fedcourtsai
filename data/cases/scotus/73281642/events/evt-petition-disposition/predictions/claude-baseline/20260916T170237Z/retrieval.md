# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "145 S. Ct. 11"` (lookup of
  the Baker v. City of McKinney denial as a known-case prior). Returned no rows.
  stderr: `ranged corpus reads: 1357 GET(s), 355532800 byte(s)` and
  `note: citations filter: 200 of 590880 rows in scope (scotus) carry citation data ...`.
  No further corpus queries were run; base rates were read from the committed
  `metrics/statpack.md` (Modern discretionary-cert petitions by disposition;
  by originating circuit; relist count; CVSG status; salience band; the
  per-Term table; Segment base rate by salience band (sal-v4)).

## CourtListener MCP

1. `search` type=d court=scotus docket_number=25-1163 (companion Pena
   petition). 0 results.
2. `get_endpoint_item` dockets item_id=73281642 (this docket; fields id,
   case_name, docket_number, date_filed, date_terminated, date_last_filing,
   date_modified). Returned: docket 25-1158, filed 2026-04-08, not terminated,
   last modified 2026-06-24.
3. `search` type=d court=scotus q=`Pena "City of Los Angeles"`
   filed_after=2026-01-01. 0 results.
4. `call_endpoint` docket-entries docket=73281642 order_by=-date_filed. 0
   results (no RECAP entries held for this SCOTUS docket).
5. `search` type=o court=ca7 case_name="Hadley v. City of South Bend". 1
   result: cluster 10692159, filed 2025-10-07, Kolar, Published, No. 24-2448.
6. `search` type=d court=scotus q="25-1163". 0 results.
7. `call_endpoint` opinions cluster=10692159 (fields id, author_str, type,
   plain_text). Returned the Seventh Circuit opinion text (Kolar, J.; panel
   Rovner, Scudder, Kolar), which I read in full.

## Web searches

None.
