# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted` (default limit 20; read the first 8 rows). stderr: `ranged corpus reads: 48 GET(s), 12451840 byte(s)`. Rows were dominated by recent grants and substantive applications; none bore a CVSG date.
2. `uv run fedcourts query --court scotus --era 2020s --limit 400`, filtered locally for rows with a non-null `cvsg_date`. stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache). 400 rows returned, 0 with a CVSG date, so no case-level CVSG priors were usable; the statpack CVSG cut stood in.

## CourtListener MCP

3. `search` (opinions, court `ca2`, q `"Mosaic Health" Sanofi 340B`): found the original (2025-08-06, cluster 10648685) and amended (2025-10-15, cluster 10704311, opinion 11170898) Second Circuit opinions in No. 24-598.
4. `read_document` (opinion 11170898, chunks 0–1 of 12 at 6000 chars): confirmed the panel (Pérez, Nathan, Kahn; opinion by Judge Pérez), the district judge (Chief Judge Wolford, W.D.N.Y.), and the holding that the proposed second amended complaint plausibly pleads a horizontal conspiracy; judgment vacated and remanded with leave to amend.
5. `search` (dockets, court `scotus`, q `"United Biologics" Amerigroup`): no results.
6. `call_endpoint` `dockets` (court `scotus`, docket_number `25-1388`): found *United Biologics, LLC v. Amerigroup Tennessee, Inc.*, docket id 73500290, filed 2026-06-16, not terminated.
7. `call_endpoint` `docket-entries` (docket 73500290): no entries available on CourtListener.

## Statpack

Read `metrics/statpack.md`: modern discretionary-cert disposition table, originating-circuit cut, relist-count cut, CVSG cut, capital-case cut, salience-band table, per-Term table, and the sal-v4 segment base rate by salience band.

No web searches were run. No retrieval touched this case's own disposition; the petition was invited today and remains pending.
