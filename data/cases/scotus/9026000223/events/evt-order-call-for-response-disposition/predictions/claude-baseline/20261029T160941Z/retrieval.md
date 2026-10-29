# Retrieval log

Corpus lookups:

1. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
   — refused with a usage error (`Unknown era 'modern'`); no rows.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. Five recent granted SCOTUS
   rows (government-party applications/petitions); none analogous, used only as
   context.
3. `uv run fedcourts query --court scotus --docket-number 26-223`
   — `ranged corpus reads: 9 GET(s), 2359296 byte(s)`. This docket's own row:
   open, no CVSG, no disposition fields — consistent with the snapshot.

Base rates: committed `metrics/statpack.md` (salience-band table, relist,
CVSG, amicus and originating-circuit cuts).

No CourtListener MCP calls and no web searches.
