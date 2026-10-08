# Retrieval log

Mode: `forward` (per `record/context.json`). No `DECIDED_BEFORE` clock.

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 28 GET(s), 7274496 byte(s)`
   Returned eight recent granted rows (immigration applications, a capital case, a redistricting application, a domestic-relations case). None comparable to a Rule 60(b)(5) mootness petition; used only to confirm the surface works. The query filters carry no text search, so no targeted comparator query was possible.

## Statpack (committed `metrics/statpack.md` / `metrics/statpack.json`)

- "Segment base rate by salience band (sal-v4)": pooled the `state` column's bracketed `reached` figures over Terms 2017–2025 → 23.6% (n=419).
- "Cert petitions by relist count (paid scored segment)" and "by CVSG status (paid scored segment)": read for shape.
- Paid-class per-Term `granted` / `gvr` counts from `statpack.json`, and `fedcourtsai.pipeline.claims.summary_route_base_rate(2026, pack)` → 0.3534, for the summary-route baseline.

## CourtListener MCP lookups

1. `search` type `o`, court `ca9`, q `"Guam Society of Obstetricians" Moylan`, filed after 2023-01-01 → one hit: the published February 3, 2026 order denying rehearing with Judge VanDyke's statement (cluster 10783407, opinion 11250043, docket 23-15602).
2. `search` type `d`, court `scotus`, docket number `26-22` → no results.
3. `search` type `o`, q `"60(b)(5)" Dobbs injunction moot abortion`, filed after 2022-06-24 → no results.
4. `read_document` opinion 11250043, chunks 0, 4, 5 of 7 (6000 chars each) → read the order, the summary, and the parts of the VanDyke statement on mootness, McCorvey, and the injunction's reach.
5. `search` type `o`, court `guam`, q `"Leon Guerrero" "20-134" repealed` → one hit: In re Request of Lourdes A. Leon Guerrero, 2023 Guam 11 (CRQ23-001, Oct. 31, 2023). Not read.
6. `search` type `d`, court `scotus`, case name `Moylan`, filed after 2026-01-01 → no results.

No web searches. Nothing retrieved concerned this petition's disposition.
