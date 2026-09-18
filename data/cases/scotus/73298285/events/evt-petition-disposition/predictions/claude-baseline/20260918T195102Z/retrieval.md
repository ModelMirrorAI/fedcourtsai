# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 8`
   `ranged corpus reads: 36 GET(s), 9437184 byte(s)`
   Returned 2020s GVR rows (Monsanto v. Salas and companions, Davis v. United States, Wells v. Texas, Lung'aho v. United States, Aquino v. United States); none Bivens-related. Used only for the shape of GVR dockets (distribution counts of 3 before the GVR).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Returned substantive applications and 2020s grants (People Not Politicians v. Onder, NRCC v. Brown, National Park Service v. National Trust, Trump v. California, Jouppi v. Alaska, Viramontes v. Cook County, Grant v. Higgins, Grand v. University Heights); none Bivens-related. Not used for the number.

## CourtListener MCP

3. `search` type=d court=scotus case_name="Mohamud v. Weyker" — 0 results.
4. `search` type=d court=scotus case_name="Nielsen v. Watanabe" — 0 results.
5. `search` type=d court=scotus docket_number=26-111 — 0 results.
6. `search` type=d court=scotus docket_number=25-417 — 0 results.
7. `search` type=d court=scotus docket_number=25-760 — 0 results.
8. `search` type=o court=ca2 q="Sigalovskaya Braden" — 1 result: Sigalovskaya v. Braden, No. 23-7625, filed 2025-08-27, published, cluster 10661588. Not opened; the provisioned petition and BIO characterize it.
9. `search` type=d court=scotus q="Watanabe" — 0 results.
10. `call_endpoint` dockets court=scotus docket_number=25-417 — Francis Nielsen v. Kekai Watanabe, docket id 73278422, filed 2025-10-07, no cert dates populated.
11. `call_endpoint` dockets court=scotus docket_number=25-760 — Hamdi A. Mohamud v. Heather Weyker, docket id 73279894, filed 2025-12-29, no cert dates populated.
12. `call_endpoint` docket-entries docket=73279894 — 0 entries.
13. `call_endpoint` docket-entries docket=73278422 — 0 entries.

No web searches. Nothing retrieved concerned this petition's own disposition; the petition is pending with a conference set for 2026-09-28.

## Committed base rates

`metrics/statpack.md`: Modern discretionary-cert petitions by disposition; relist-count and CVSG cuts (paid scored segment); salience-band cut; SCOTUS cert petitions by Term; Segment base rate by salience band (sal-v4), Term rows 2017 through 2024.
