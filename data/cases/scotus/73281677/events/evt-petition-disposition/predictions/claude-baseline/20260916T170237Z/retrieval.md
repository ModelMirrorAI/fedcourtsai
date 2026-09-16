# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts query --court scotus --disposition granted --limit 8`
  - stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  - Returned 8 rows: four substantive OT2025 applications (People Not Politicians v. Onder; NRCC v. Brown; National Park Service v. National Trust for Historic Preservation; one further election-related application) and four cert grants (Jouppi v. Alaska; Viramontes v. Cook County; Grant v. Higgins; one religious-liberty matter). Used only as a sanity check on the grant population; none is a CAAF prior.

## CourtListener MCP

- `search` type=d court=scotus docket_number=25-742 → 0 results (search index does not carry these dockets).
- `search` type=d court=scotus docket_number=25-685 → 0 results.
- `search` type=d court=scotus docket_number=25-1148 → 0 results.
- `call_endpoint dockets` court=scotus docket_number=25-742 → Zhuo H. Zhong v. United States, id 73279874, filed 2025-12-22, date_terminated null.
- `call_endpoint dockets` court=scotus docket_number=25-685 → Robert D. Schneider v. United States, id 73279533, filed 2025-12-11, date_terminated null (the BIO records this petition as denied January 12, 2026; CourtListener does not populate termination for these SCOTUS dockets).
- `call_endpoint dockets` court=scotus docket_number=25-730 → Jennesis V. Dominguez-Garcia v. United States, id 73279861, filed 2025-12-19, date_terminated null.
- `get_endpoint_item dockets` 73281677 → this docket; date_modified 2026-06-17, date_terminated null. No disposition has surfaced; conference is September 28, 2026.
- `call_endpoint docket-entries` docket=73279874 (Zhong) → 0 entries.

## Web

None.

## Statpack

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Petitions by originating court" (CAAF row), "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `baseline` reached rate over OT2017–OT2024).
