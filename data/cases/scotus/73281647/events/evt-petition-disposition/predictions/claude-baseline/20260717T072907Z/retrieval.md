# Retrieval log — scotus/73281647 / evt-petition-disposition / claude-baseline / 20260717T072907Z

Provisioned inputs read: the 2026-07-17 snapshot, `record/documents/`
(questions-presented.txt, petition.txt, brief-in-opposition.txt,
documents.json), `record/context.json` (mode: forward), and the committed
`metrics/statpack.md` for base rates (Modern discretionary-cert disposition,
originating-circuit, relist, CVSG, and per-Term tables; this statpack version
carries no salience-band table).

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "594 U.S. 139" --citation "505 U.S. 1003" --citation "145 S. Ct. 11" --limit 8`
   → 0 rows.
   `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
2. `uv run fedcourts query --court scotus --topic takings --era 2020s --limit 8`
   → 0 rows.
   `ranged corpus reads: 3 GET(s), 786432 byte(s)`

Neither query surfaced matching priors, so the quantitative anchor rests on the
committed statpack alone.

## CourtListener MCP lookups

None. The provisioned record (snapshot current as of today, full petition, BIO,
and QP text) covered the pre-decision record; the case's own outcome cannot
exist yet (conference set for 2026-09-28) and was not sought.

## Web searches

None.
