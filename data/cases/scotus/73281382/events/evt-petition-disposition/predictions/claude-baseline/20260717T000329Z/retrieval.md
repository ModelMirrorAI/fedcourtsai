# Retrieval log — scotus/73281382, evt-petition-disposition, claude-baseline, 20260717T000329Z

Beyond the provisioned inputs (snapshot, questions-presented, petition, BIO) and
the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "569 U.S. 1" --citation "584 U.S. 586" --limit 8`
   — 0 rows returned.
   `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --citation "Jardines" --era 2020s --limit 8`
   — 0 rows returned.
   `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

## CourtListener MCP lookups

1. `search` (type=docket, court=scotus, q="knock and talk") — 0 results; no
   companion or related SCOTUS dockets surfaced. No information about this
   case's own disposition was sought or found (forward cell; the petition is
   pending, distributed for the 9/28/2026 conference).

## Web searches

None.
