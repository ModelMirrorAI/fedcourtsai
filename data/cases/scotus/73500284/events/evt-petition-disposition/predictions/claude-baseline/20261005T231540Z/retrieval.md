# Retrieval log

## Corpus lookups (`fedcourts query`, through the cell's corpus service)

1. `uv run fedcourts query --court scotus --citation "590 U.S. 432" --citation "556 U.S. 624"`
   stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)` plus a `note:`
   line that only 200 SCOTUS rows carry any citation and the filter matches a
   case's own cites. Zero rows.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   stderr: `ranged corpus reads: 25 GET(s), 6422528 byte(s)`. Eight rows, mostly
   emergency applications and federal-party petitions; none on arbitration.
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 80`
   (output filtered locally for captions containing arbitration, insurance,
   underwriter, or Lloyd)
   stderr: `ranged corpus reads: 46 GET(s), 12058624 byte(s)`. Zero matching
   captions.

Base rates: the committed `metrics/statpack.md`, sections "Modern
discretionary-cert petitions by disposition", "Modern cert petitions by
originating circuit", "Cert petitions by relist count", "by CVSG status",
"by salience band", and "Segment base rate by salience band (sal-v4)".

## CourtListener MCP lookups

4. `get_endpoint_item` dockets 73500284: docket 25-1383, filed 2026-06-15,
   not terminated, last modified 2026-09-09.
5. `call_endpoint` docket-entries for docket 73500284: zero entries held.
6. `search` opinions, ca7, q "Jump Trading" estoppel Convention "Arthur
   Andersen": zero hits.
7. `search` opinions, case_name "Kim v. Jump Trading", filed after 2026-01-01:
   one hit, Taewoo Kim v. Jump Trading, LLC, No. 25-1964 (7th Cir. Aug. 13,
   2026), cluster 10947384.
8. `call_endpoint` opinions, cluster 10947384: one opinion (id 11414970,
   author Easterbrook); plain text is font-encoding garbage, unreadable.
9. `read_document` opinion 11414970, chunks 0-2: same garbled text. Stopped
   retrying; relied on the BIO's quotations of Kim.

## Web fetch

10. `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1383.html`
    (forward-mode check of the live docket): twelve entries, identical to the
    snapshot, ending with the Sep 9 reply; no redistribution, no order.
