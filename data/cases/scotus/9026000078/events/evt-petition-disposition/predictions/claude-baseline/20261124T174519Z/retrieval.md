# Retrieval log

Beyond the provisioned inputs:

- `metrics/statpack.md` — read the salience-band table (elevated column) and the relist-count cut (paid scored segment).
- `uv run fedcourts query --help` — usage.
- `uv run fedcourts query --court scotus --docket-number 25-6623` — Kian v. Florida row (granted 2026-06-15, distribution_count 5, merits brief filed 2026-09-28, undecided). stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. Run a second time to print the row's fields (stderr suppressed that time).
- `uv run fedcourts query --court scotus --docket-number 26-76` — Jackson v. Florida row (pending, companion). stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`.
- `uv run fedcourts query --court scotus --disposition granted --era modern` — refused: unknown era token `modern` (usage error); not retried.

No CourtListener MCP calls and no web searches.
