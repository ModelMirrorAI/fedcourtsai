# Retrieval log — claude-baseline, scotus/73500252, 20260820T181919Z

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-20.json`,
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`,
`documents.json`, `record/context.json`) and the committed
`metrics/statpack.md`, I consulted:

## Corpus lookups (`fedcourts query`)

Both attempts failed on the corpus service's read timeout; no priors were
retrieved and no `ranged corpus reads:` line was printed on either.

1. `fedcourts query --court scotus --citation "602 U.S. 205"` (looking up the
   corpus row for *Cantero v. Bank of America* as a directly analogous
   resolved prior) — stderr:
   `corpus service at http://127.0.0.1:8377 timed out after 180s — a slow corpus read, not a dead sidecar: ReadTimeout('timed out')`
2. Same command, retried — same 180s ReadTimeout, same stderr line.

## CourtListener MCP lookups

1. `search` (type `d`, court `scotus`, case_name `Cantero`) — attempting to
   verify the docketing status of the companion *Cantero III* cert petition
   the BIO reports as pending. **0 results**; the docket search index does not
   appear to cover scraped SCOTUS dockets. No further MCP calls made — the
   BIO's July 30, 2026 account of the three pending petitions stands as the
   evidence. Nothing outcome-revealing was surfaced (the petition's first
   conference, September 28, 2026, post-dates this run).

## Web searches

None.
