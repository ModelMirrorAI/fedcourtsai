# Retrieval log

- Read committed `metrics/statpack.md`: modern-cert dispositions, originating
  circuit, paid-segment relist/CVSG cuts, and sal-v4 prior-Term reached bands.
  Read `metrics/statpack.json` to pool exact baseline reached rates and weighted
  denominators for 2017–2025. Result: 638 / 12,720 = 0.05015723270440252.
- Ran `git log -1 --format='%cs %h' -- metrics/statpack.md` for artifact vintage:
  `2026-09-26 96ebdd342`. No remote corpus freshness was inferred.
- General web searches: `site.supremecourt.gov "T. M." "Medical System" "2026"`
  and `site.supremecourt.gov "Skinner" "independent claim" "562"`. The tool
  returned no usable results. An attempted open of the Supreme Court opinion
  path `opinions/25pdf/25-197_bp7c.pdf` also returned no usable content. Neither
  search named this petition or sought its outcome.
- CourtListener MCP `search`, type `o`, court `scotus`, query
  `"T. M." "University of Maryland"`, limit 3: returned the June 18, 2026
  decision in No. 25-197 and its June 19 revision (clusters 10876934 and
  10877643; opinions 11344435 and 11345156).
- CourtListener MCP `read_document`, opinion 11345156, chunk index 0,
  chunk size 18000: consulted the syllabus and opening majority text for the
  general Rooker-Feldman timing holding. This is a different case decided
  before the provisioned snapshot, not Loop's own outcome.
- No `fedcourts query` or `open-events` corpus retrieval was used, so there is
  no ranged-corpus transfer line. The paths helper was run with the cell's
  literal identifiers; its initial cache error was resolved with a temporary
  writable cache and `--no-sync`. No evaluator-only file was read.
