# Retrieval log — scotus/73281354, evt-petition-disposition, claude-baseline, 20260717T000329Z

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "431 U.S. 720" --citation "550 U.S. 544" --era 2020s --limit 8`
   → 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --citation "550 U.S. 544" --limit 8`
   → 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
3. `uv run fedcourts query --court scotus --topic antitrust --limit 8`
   → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
4. `uv run fedcourts query --court scotus --topic Antitrust --limit 8`
   → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   → 5 rows (recent granted petitions; sanity check on grant-signal shape — distribution
   counts, top counsel). `ranged corpus reads: 145 GET(s), 37879808 byte(s)`

No close antitrust priors surfaced; base rates came from the committed
`metrics/statpack.md` and `metrics/statpack.json` (Term 2025 paid-class grant rate,
relist/CVSG/circuit cuts).

## CourtListener MCP lookups

1. `search(type=d, court=scotus, q="Academy of Allergy" OR "Amerigroup")` → 0 results.
   Checked whether a companion cert petition from the Sixth Circuit's *Academy of
   Allergy v. Amerigroup* case is docketed (grant/hold dynamics for QP1). None found.
2. `search(type=d, court=scotus, docket_number=25-1070)` → 0 results (SCOTUS dockets
   are not in the RECAP index; petition status taken from the provisioned snapshot).

## Web searches

None.
