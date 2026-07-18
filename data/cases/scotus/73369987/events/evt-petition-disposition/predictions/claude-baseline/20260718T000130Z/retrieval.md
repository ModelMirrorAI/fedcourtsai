# Retrieval log — scotus/73369987 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Beyond the provisioned inputs (snapshot, petition text, event definition) and
the committed `metrics/statpack.md` / `metrics/statpack.json` base rates:

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era modern --limit 8`
   - stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
   - 0 rows (the corpus era labels are decade strings like `2020s`, not `modern`).
   - Re-run of the same command to separate stdout/stderr streams:
     stderr: `ranged corpus reads: 430 GET(s), 112590848 byte(s)` — 0 rows again.
2. `uv run fedcourts query --court scotus --limit 5`
   - stderr: `ranged corpus reads: 430 GET(s), 112590848 byte(s)`
   - 5 rows returned (recent resolved/granted/denied SCOTUS petitions with
     distribution counts); used as a sanity check on the relist/distribution
     signal, not as case-specific priors — no facet in the corpus rows matches
     a pro se state-court family-law petition closely.

## CourtListener MCP

None. The provisioned snapshot is dated 2026-07-17 (one day old), the cell is
`forward` with the conference date (2026-09-28) still in the future, and the
petition text was provisioned in full, so no live docket lookup was needed.

## Web searches

None.
