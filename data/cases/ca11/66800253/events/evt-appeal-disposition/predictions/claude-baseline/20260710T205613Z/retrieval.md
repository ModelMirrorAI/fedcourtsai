# Retrieval log — ca11/66800253 evt-appeal-disposition, claude-baseline, 20260710T205613Z

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court ca11 --corpus-backend ranged`
   - `ranged corpus reads: 44 GET(s), 11534336 byte(s)`
   - Purpose: surface CA11 resolved priors. Results were noisy (rows with
     unrelated opinion text misjoined onto ca11 docket ids); used only as a
     data-quality signal, not as substantive priors.
2. `uv run fedcourts query --court ca11 --disposition granted --corpus-backend ranged`
   - `ranged corpus reads: 109 GET(s), 28573696 byte(s)`
   - Purpose: inspect what `granted`-labeled CA11 rows look like. The top rows
     were visibly misjoined (19th-century state-court text), confirming the
     ca11 priors surface is unreliable; disregarded for the merits call.

## Base rates

- `metrics/statpack.md` (committed roll-up): the by-court table's CA11 row
  (45 resolved: other 95.6%, denied 2.2%, granted 2.2%) anchored the
  label-space prior.

## CourtListener MCP

None — the configured CourtListener MCP server never connected in this cell
(no `courtlistener` tools were discoverable), so no CourtListener retrieval
was possible. Flagged in `flags.json`.

## Web searches

None — deliberately. The provisioned snapshot shows an opinion already issued
on this docket (entry #37, 2025-04-10), so any web or docket search on this
case would risk surfacing its actual disposition, which the contract forbids
seeking. The prediction rests on the provisioned snapshot, the statpack, and
repo-internal inspection of the disposition-labeling code
(`src/fedcourtsai/pipeline/ingest.py`, `src/fedcourtsai/pipeline/outcome.py`,
`.github/prompts/reconcile.md`).
