# Retrieval log

Beyond the provisioned inputs (snapshot, `event.yaml`, `record/context.json`,
`record/documents/` petition + questions-presented, and the committed
`metrics/statpack.md`):

## Corpus lookups (`fedcourts query`, service backend)

1. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5 --corpus-backend service`
   — 0 rows (era value matched nothing).
   `ranged corpus reads: 747 GET(s), 195821568 byte(s)`
2. Re-run of the same command (output-capture retry) — 0 rows.
   `ranged corpus reads: 711 GET(s), 186384384 byte(s)`
3. `uv run fedcourts query --court scotus --disposition granted --limit 5 --corpus-backend service`
   — 5 granted priors (Jouppi v. Alaska; Viramontes v. Cook County; Grant v.
   Higgins; one additional granted petition; Apple v. Epic Games). Generic
   grants only — the filter surface cannot select federal-petitioner or
   statute-invalidation priors, so these did not move the estimate.
   `ranged corpus reads: 5 GET(s), 1310720 byte(s)`

## CourtListener MCP lookups

4. `search` (type=d, court=scotus, docket_number="26-93") — 0 results.
5. `search` (type=d, court=scotus, q='Ream "Department of the Treasury"') — 0
   results. Both sought the companion petition *Ream v. Department of the
   Treasury*, No. 26-93 (a pending companion case, legitimate forward signal);
   CourtListener's docket index did not surface it, so the companion posture
   rests on the provisioned petition's own statements.

No web searches. No lookup sought this case's own disposition (none can exist:
the petition was docketed two days before this run and the response is not yet
due).
