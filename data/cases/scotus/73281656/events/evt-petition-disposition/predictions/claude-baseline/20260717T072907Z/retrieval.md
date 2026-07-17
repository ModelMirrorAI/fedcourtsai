# Retrieval log — scotus/73281656 / evt-petition-disposition / claude-baseline / 20260717T072907Z

Forward-mode cell. Retrieval beyond the provisioned inputs:

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "Strickland v. Washington" --citation "Thornell v. Jones" --era 2020s`
   → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
   (run twice — once with stderr discarded — so two ranged-read sessions of the same shape)
2. `uv run fedcourts query --court scotus --citation "Strickland" --era 2020s --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --limit 5` (sanity check that the query surface works)
   → 5 rows returned (unrelated 2020s cert dockets; confirmed corpus rows carry empty `citations` lists). stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
4. `uv run fedcourts query --court scotus --citation "466 U.S. 668" --limit 8`
   → 0 rows. stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`

Citation-based prior retrieval surfaced nothing (ingested SCOTUS rows have no
populated citation lists), so no case-level corpus priors informed the
probability; the sanity-check rows were not used as priors.

## Base rates

- Committed `metrics/statpack.md` — "Modern discretionary-cert petitions by
  disposition", originating-court, relist, and CVSG cuts; per-Term table.
- Committed `metrics/statpack.json` — per-Term fee-class detail (Term 2025:
  paid grant ≈ 5.4%, IFP grant ≈ 1.1%). No salience-band segment table is
  present in the committed statpack.

## CourtListener MCP

None — the provisioned snapshot and filed-document texts were sufficient, and
this case's own disposition does not yet exist (conference set for
2026-09-28), so no live docket lookups were needed.

## Web searches

None.
