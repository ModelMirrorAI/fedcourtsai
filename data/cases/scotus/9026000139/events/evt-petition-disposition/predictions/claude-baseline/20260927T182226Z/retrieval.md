# Retrieval log — claude-baseline / 20260927T182226Z / scotus/9026000139

Beyond the provisioned inputs (snapshot 2026-09-27.json, context.json, petition.txt, questions-presented.txt, brief-in-opposition.txt) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --disposition gvr --limit 12`
   stderr: `ranged corpus reads: 42 GET(s), 10878976 byte(s)`
   Returned recent GVR priors; three Monsanto rows (Salas 24-1097, Johnson 24-1098, Anderson 25-1042) all `gvr`, cert granted 2026-06-30.
2. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 40`
   stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   Read the full row fields for the three Monsanto GVRs: counsel (Clement), originating courts (CA11, Oregon Ct. App., Missouri Ct. App.), distribution counts (4, 4, 2), `distributed_for_conference` 2026-06-29, `last_live_polled` 2026-08-03.
3. `uv run fedcourts open-events --court scotus` — errored (requires `--docket`); not used.

## CourtListener MCP lookups

4. `search` type=d, court=scotus, party_name=Monsanto, filed_after=2026-01-01 — 0 results.
5. `search` type=d, court=scotus, q=Monsanto, filed_after=2025-01-01 — 0 results (SCOTUS docket index does not surface these).
6. `search` type=o, court=scotus, q="Monsanto Durnell", filed_after=2026-06-01 — 1 result: Monsanto v. Durnell, 24-1068, cluster 10880244, decided 2026-06-25.
7. `search` type=o (same query) with `opinions` field — opinion id 11347763, author Kavanaugh, combined opinion, 609 U.S. ___.
8. `read_document` opinion_id=11347763, chunk 0 of 15 (syllabus): held FIFRA expressly preempts the label-based failure-to-warn claim under §136v(b); Bates and Riegel relied on.

No web searches. No lookup of this case's own docket beyond the provisioned snapshot, and no search for its disposition.
