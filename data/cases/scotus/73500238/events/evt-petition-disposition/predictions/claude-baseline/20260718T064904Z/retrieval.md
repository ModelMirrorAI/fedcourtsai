# Retrieval log — scotus/73500238, evt-petition-disposition, claude-baseline, 20260718T064904Z

Beyond the provisioned inputs (snapshot `2026-07-18.json`, `questions-presented.txt`,
`petition.txt`, `documents.json`) and the committed `metrics/statpack.md` base rates:

## Corpus lookups

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   — `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   Purpose: recent granted-petition priors; confirmed recent grants typically carry
   multiple conference distributions (distribution_count 3–22) before the grant.

## CourtListener MCP lookups

2. `search(type=d, court=scotus, case_name="Holmes v. United States", filed_after=2026-01-01)`
   — 0 results.
3. `search(type=d, court=scotus, q="Elizabeth Holmes")` — 0 results.
   Purpose (both): check whether a companion Elizabeth Holmes cert petition is
   docketed (linked-case grant pressure). None found. This case's own disposition
   was never queried; the case is pending (forward mode, first conference 2026-09-28).

## Web searches

None.
