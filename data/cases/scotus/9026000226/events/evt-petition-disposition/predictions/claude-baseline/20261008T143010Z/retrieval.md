# Retrieval log

## Corpus (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   stderr: `ranged corpus reads: 28 GET(s), 7274496 byte(s)`
   Returned six recent granted rows (Missionaries of Saint John the Baptist v.
   Frederic 25-1131; Marschner v. Marschner 25-1349; Rhoney v. Barbosa da Cunha
   26-104; Nelsen v. Pike 26A428; DHS v. D.V.D. 26-426 and 26A406). No subject
   filter exists on `query`, so none were topically comparable; not used for the
   number.
2. The same command re-run to format the rows (stderr not captured on the re-run;
   a warm service cache may have served it).

## CourtListener MCP (5 calls)

1. `search` type=d court=scotus docket_number=26-226 → 0 results.
2. `search` type=d court=scotus docket_number=26-164 → 0 results.
3. `search` type=d court=scotus q=Mast filed_after=2026-06-01 → 0 results.
4. `search` type=o court=ca4 q="Doe v. Mast" filed_after=2026-01-01 → 1 result:
   Baby Doe v. Joshua Mast, No. 24-1900, filed 2026-04-22, status Published
   (cluster 10847356). Confirms the published, dated opinion below. Not opened.

## Base rates

Committed `metrics/statpack.md`: modern discretionary-cert disposition table;
relist-count, CVSG, and originating-circuit cuts; "Segment base rate by salience
band (sal-v4)" table, `baseline` column, bracketed `reached` figures pooled over
OT2017–OT2025.

## Web search

None.
