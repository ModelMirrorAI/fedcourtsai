# Retrieval log

## Corpus (`fedcourts`, via the cell's corpus service)

- `uv run fedcourts paths --court scotus --docket 9026000443 --event evt-petition-disposition --role predictor`
- `uv run fedcourts open-events --court scotus --docket 9026000360` -> `evt-petition-disposition` (FedEx v. Watt, No. 26-360, is in the corpus with an open event)
- `uv run fedcourts open-events --court scotus --docket 9026000387` -> `evt-petition-disposition` (Kellogg v. Reichert, No. 26-387, likewise)
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s` -> 20 rows; stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (used for the distribution-count shape of held-then-GVR'd petitions)
- `uv run fedcourts query --court scotus --era 2020s --disposition granted` -> 20 rows; stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
- Committed `metrics/statpack.md`: modern-cert disposition, originating-circuit, relist-count, CVSG, salience-band, per-Term, and the sal-v4 segment-by-band tables.

## CourtListener MCP

- `search` type=d court=scotus docket_number=26-360 -> 0 results
- `search` type=d court=scotus docket_number=26-387 -> 0 results
- `search` type=o q="actuarial equivalent" "1055(d)" Kellogg Reichert courts ca6,ca11 -> 0 results
- `call_endpoint` dockets court=scotus docket_number=26-360 -> 0 results
- `call_endpoint` dockets court=scotus docket_number=26-387 -> 0 results
- `search` type=o case_name="Reichert v. Kellogg" court=ca6 -> cluster 10809377, filed 2026-03-16, docket 24-1442
- `search` type=o case_name="Drummond v. Southern Company Services" court=ca11 -> cluster 10864256, filed 2026-05-26, docket 24-12773
- `call_endpoint` clusters id=10809377 -> judges Stranch, Bush, Nalbandian; published

## Web

- WebSearch (extended): FedEx v. Watt 26-360 actuarial equivalence ERISA 1055(d)
- WebSearch (standard): Reichert v. Kellogg Sixth Circuit cert petition 2026
- WebSearch (standard): ERISA actuarial equivalence appeals pending 2026 (surfaced the April 2026 Intel district-court ruling for the sponsor and the Sixth Circuit en banc denial of May 15, 2026)
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-360.html (docketed 2026-09-16, response due 2026-10-16, waiver filed 2026-09-24, no distribution shown)
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-387.html (docketed 2026-09-22, response due 2026-10-22, waiver filed 2026-09-25, no distribution shown)

Nothing retrieved concerned this case's own disposition.
