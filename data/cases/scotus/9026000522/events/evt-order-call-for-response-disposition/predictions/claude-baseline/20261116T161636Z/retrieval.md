# Retrieval log

Corpus lookups (via the cell's corpus service):

1. `uv run fedcourts query --help` — read the interface.
2. `uv run fedcourts query --court scotus --docket-number 25-819` — `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. Returned *Hedgepeth v. Britton*: 7th Cir., denied 2026-05-18, distribution_count 2, seven amicus counsel listed.
3. `uv run fedcourts query --court scotus --docket-number 24-355` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned *MacRae v. Mattos*: 1st Cir., denied 2025-06-30, distribution_count 16.
4. `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 3` — usage error (unknown era token; the era vocabulary is decades). Not re-issued; the two docket lookups were the priors I needed.
5. `uv run fedcourts query --court scotus --docket-number 25-819` again (stderr discarded) to read the distribution fields.

Base rates: `metrics/statpack.md` (salience-band table sal-v8, relist-count cut, amicus-count cut, originating-court table).

No CourtListener MCP calls and no web searches. The live Supreme Court docket was not consulted.
