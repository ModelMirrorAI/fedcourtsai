# Retrieval log — claude-baseline / 20260710T234542Z

## Provisioned inputs (baseline)

- `record/snapshots/2026-07-10.json` — docket snapshot (No. 25-1231).
- `record/documents/questions-presented.txt`, `record/documents/petition.txt`
  (46 pp., not truncated), `record/documents/documents.json`. No
  brief-in-opposition was provisioned (respondents waived; the Court's
  requested response is not yet filed).
- `record/context.json` — mode `forward`.
- `events/evt-petition-disposition/event.yaml`.

## Corpus lookups (`fedcourts` CLI, ranged backend)

1. `uv run fedcourts query --court scotus --citation "518 U.S. 839"
   --citation "431 U.S. 1" --citation "10 U.S. 87" --limit 8
   --corpus-backend ranged` — no matching priors returned.
   stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
2. `uv run fedcourts query --court scotus --citation "433 U.S. 425"
   --citation "468 U.S. 841" --citation "328 U.S. 303" --limit 8
   --corpus-backend ranged` — no matching priors returned.
   stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --limit 8
   --corpus-backend ranged` — 8 resolved 2020s SCOTUS priors (7 denied,
   1 granted), including several distributed for the same 6/25/2026
   conference this petition was initially distributed for.
   stderr: `ranged corpus reads: 378 GET(s), 99090432 byte(s)`

## Base rates

- Committed `metrics/statpack.md` — overall SCOTUS resolved base rate and
  Term/circuit tables. The "Modern discretionary-cert petitions by
  disposition" section referenced by the predict prompt is not present in
  the committed statpack (see `flags.json`).

## CourtListener MCP

- Attempted `search` (opinions, `"Hastings College Conservation
  Committee"`) and `search` (dockets, scotus, `25-1231`): **both failed**
  with a server-side error (`REDIS_URL is not set; cannot access session
  store`). No CourtListener data was retrieved this run; the cell proceeded
  on provisioned inputs and corpus tooling.

## Web searches

None.
