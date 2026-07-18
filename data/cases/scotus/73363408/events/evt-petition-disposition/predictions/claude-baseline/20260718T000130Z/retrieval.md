# Retrieval log — scotus/73363408, run 20260718T000130Z

Beyond the provisioned inputs (snapshot, questions-presented, petition text) and
the committed `metrics/statpack.md`:

1. `uv run fedcourts query --court scotus --era modern --limit 5`
   - `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
   - Returned no rows (`--era` takes decade labels like `2020s`, not `modern`).
2. `uv run fedcourts query --court scotus --era modern --limit 5` (rerun while
   separating stdout/stderr)
   - `ranged corpus reads: 430 GET(s), 112590848 byte(s)`
   - No rows, same reason.
3. `uv run fedcourts query --court scotus --limit 5`
   - `ranged corpus reads: 430 GET(s), 112590848 byte(s)`
   - Returned 5 recent resolved/near-resolved SCOTUS priors (e.g. Monsanto v.
     Salas — granted after 4 distributions; McCoy v. ATF — denied after 3
     distributions; Oregon v. Maney — dismissed), consistent with the statpack
     pattern that grants ride on multiple distributions/relists while this
     petition has a single long-conference distribution.

No CourtListener MCP lookups and no web searches — the provisioned snapshot is
one day old, the conference date (2026-09-28) is in the future, and the
petition's defects are dispositive on the provisioned record.
