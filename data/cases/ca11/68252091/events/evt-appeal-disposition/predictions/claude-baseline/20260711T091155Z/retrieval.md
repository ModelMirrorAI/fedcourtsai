# Retrieval log — claude-baseline / 20260711T091155Z

## Corpus lookups

- `uv run fedcourts query --court ca11 --corpus-backend ranged`
  - stderr: `ranged corpus reads: 45 GET(s), 11796480 byte(s)`
  - Returned 20 resolved ca11 priors, ranked; 19 labeled `other`, 1 `denied`.
    Mostly merits appeals, no original mandamus proceedings — used only as a
    weak sanity check on the ca11 disposition mix.

## Base rates

- Read the committed `metrics/statpack.md` (overall base rate and the
  "Cases by court" ca11 row: 45 resolved — other 95.6%, denied 2.2%,
  granted 2.2%).

## CourtListener MCP

Attempted and unavailable — the server returned `REDIS_URL is not set; cannot
access session store` on every call:

- `search(type=d, court=flnd, docket_number=4:22-cv-00439, fields=[docket_id, caseName, court_id, dateFiled, assignedTo, suitNature, cause, docketNumber])` — failed
- `search(type=d, court=flnd, q=DeBose, fields=[docket_id, caseName, dateFiled, suitNature, cause])` — failed

Both calls targeted the *underlying district case* (to characterize what the
mandamus petition challenges), not this proceeding's outcome. No CourtListener
data was obtained.

## Web searches

None.
