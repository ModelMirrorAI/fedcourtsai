# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --disposition denied --era 2020s`
   stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   Returned 11 rows, all recent substantive stay applications (26A-series), not cert petitions; not used beyond confirming vintage.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s`
   stderr: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   Returned recent granted applications and merits-track cert grants (e.g. 25-246, 25-238, 25-566, 25-965, 25-1311); none comparable to a state-court Fourth Amendment petition; used only for shape.

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)". The "Petitions by originating court" cut has no Pennsylvania bucket.

## CourtListener MCP lookups (forward mode; 6 calls)

1. `search` type=d, court=scotus, docket_number=25-1277: 0 results.
2. `get_endpoint_item` dockets/73331499: case name, docket 25-1277, date_filed 2026-05-12, date_terminated null, date_modified 2026-06-24. No outcome present.
3. `call_endpoint` docket-entries, docket=73331499: 0 entries.
4. `search` type=o, court=pasuperct, q="Williams" DNA "John Doe" warrant particularity Parabon, filed Jul-Aug 2025: 0 results.
5. `search` type=o, citation="342 A.3d 742": 0 results.
6. `search` type=o, q="Commonwealth v. Williams" "544 MDA 2024": 0 results.

The opinion below is not on CourtListener; it was read only through the petition. No web searches were made.
