# Retrieval log

Forward-mode cell. Retrieval stayed well under the 25-call budget (2 corpus queries, 4 CourtListener MCP searches).

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Returned recent granted SCOTUS rows (substantive applications and cert petitions, e.g. People Not Politicians v. Onder, NRCC v. Brown, Jouppi v. Alaska, Viramontes v. Cook County). Used only as a shape check on what recent grants look like; none is topically similar.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned recent denied rows; same limited use.

## CourtListener MCP

3. `search` type=d, court=scotus, docket_number=25-1242 → 0 results (CourtListener does not hold this Supreme Court docket).
4. `search` type=o, q=`"intentional misuse of his vehicle" "qualified immunity" "substantive due process"`, filed_after 2019-01-01 → 0 results.
5. `search` type=o, q=`"Hughes v. Locure"` → 2 results, both later CA11 opinions citing it (Marbut v. Phillips, 2026-05-22; Acevedo v. Diaz de la Portilla, 2026-08-26). Not opened.
6. `search` type=o, published only, filed_after 2020-01-01, q=`"Browder v. City of Albuquerque" AND "clearly established" AND (speeding OR "police vehicle" OR "patrol car") AND "no emergency"` → 2 results: Hughes v. Locure (CA11, 2026-01-29) and Dean v. McKinney, 976 F.3d 407 (CA4, 2020-10-02). Used to gauge the depth of the asserted circuit split.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit", the paid scored segment's relist-count and CVSG cuts, "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `baseline` bracketed `reached` over Terms 2017–2024).

No web searches. Nothing under `data/qp-topics/` was read. No search surfaced this petition's disposition (none exists yet; first conference is 2026-09-28).
