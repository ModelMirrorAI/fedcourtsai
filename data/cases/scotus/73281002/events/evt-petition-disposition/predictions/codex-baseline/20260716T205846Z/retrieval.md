# Retrieval

## Committed base-rate material

- Consulted `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist, CVSG, and Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate (5.36%).

## Corpus lookup

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic 'election law mail voting Anderson Burdick' --era 2020s --limit 8`
- Result: failed before returning priors because the ranged corpus remote hostname could not be resolved (`EndpointConnectionError`). No `ranged corpus reads: ...` line was produced.

## CourtListener MCP lookups

- Opinion search: `q="Eakin Pennsylvania mail ballot date requirement Anderson Burdick"`, court `ca3`, filed before 2026-07-17, five results requested. Returned the published panel and rehearing materials in Third Circuit No. 25-1644.
- Repeated the same Eakin opinion search with `cluster_id` and nested `opinions` fields, three results requested, to identify the panel and rehearing records.
- SCOTUS opinion search: `q="\"Anderson-Burdick\" election regulation"`, filed 2020-01-01 through 2026-07-16. Returned no results.
- SCOTUS opinion search: `q="Anderson Burdick election regulation voting burden"`, filed 2020-01-01 through 2026-07-16. Returned no results.
- SCOTUS opinion search by case name `Brnovich`, filed 2020-01-01 through 2026-07-16. Returned *Brnovich v. Democratic National Committee*, 594 U.S. 647 (2021), and a related record.
- Opinion search: `q="McDonald mail voting rational basis Anderson Burdick"`, filed 2000-01-01 through 2026-07-16, ten results requested. Returned, among others, the Seventh Circuit's *Indiana Vote by Mail, Inc. v. Okeson* and the Sixth Circuit's *Mays v. LaRose*.
- Opinion search: `q="\"consequence of noncompliance\" voting burden ballot"`, filed 2000-01-01 through 2026-07-16. Returned the Third Circuit decision and *Arizona Democratic Party v. Hobbs*, 18 F.4th 1179 (9th Cir. 2021).

No web search or direct REST fallback was used, and no lookup sought this petition's disposition.
