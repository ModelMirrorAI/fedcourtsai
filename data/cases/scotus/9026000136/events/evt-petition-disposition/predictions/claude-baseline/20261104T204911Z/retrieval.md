# Retrieval log

Corpus lookups (companion dockets named in the cert reply, fn. 3):

- `uv run fedcourts query --court scotus --docket-number 26-73` → `ranged corpus reads: 14 GET(s), 3670016 byte(s)`. Intel v. Squires: pending, distribution_count 0, last polled 2026-11-02.
- `uv run fedcourts query --court scotus --docket-number 25-1230` → `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Google v. VirtaMove: **denied 2026-10-19**, 2 distributions, no CVSG.
- `uv run fedcourts query --court scotus --docket-number 26-198` → `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Kahoot! v. Interstellar: pending, not yet distributed.
- I re-ran the same three queries with stderr discarded, to print the rows without the attorney lists. They returned the same rows.
- `uv run fedcourts query --help` (usage only).

Base rates came from the committed `metrics/statpack.md`: the salience-band table, and the relist-count and amicus cuts.

No CourtListener MCP or web calls.
