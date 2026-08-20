# Retrieval log

Beyond the provisioned inputs (snapshot 2026-06-23, `event.yaml`,
`record/context.json`, and the three provisioned documents — questions
presented, petition, brief in opposition) and the committed
`metrics/statpack.md`, I made three `fedcourts query` corpus lookups and no
CourtListener MCP or web retrievals.

1. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
   — returned zero rows (`modern` is not a decade-era value; my error).
   stderr: `ranged corpus reads: 747 GET(s), 195821568 byte(s)`
2. Same command re-run to confirm the empty result and capture the exit code —
   zero rows again.
   stderr: `ranged corpus reads: 711 GET(s), 186384384 byte(s)`
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   — returned 5 recent granted SCOTUS priors (used as texture on what
   currently granted paid petitions look like: distribution counts, salience
   scores, counsel).
   stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`

Base rates and cuts (modern-cert disposition table, relist and CVSG cuts,
salience band table) were read from the committed `metrics/statpack.md`, not
from live retrieval.
