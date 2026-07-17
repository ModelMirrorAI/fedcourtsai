# Retrieval log — scotus/73281394 / evt-petition-disposition / claude-baseline / 20260717T000329Z

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "567 U.S. 460" --citation "593 U.S. 98" --citation "577 U.S. 190" --limit 8`
   — returned **0 rows**.
   stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --citation "567 U.S. 460" --limit 8`
   — returned **0 rows** (citation-linked priors for the Miller line appear
   not to be indexed for these petitions).
   stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

Base rates were taken from the committed `metrics/statpack.md` (modern
discretionary-cert disposition split, relist-count and CVSG cuts, per-Term
table). This statpack revision carries no per-Term salience-band table, so the
relist-0 bucket (~0.8% grant) and the modern-cert anchor (~2.5–3.3%) served as
the quantitative anchors instead.

## CourtListener MCP lookups

1. `search(type="d", court="scotus", docket_number="25-1115")` — **0 results**;
   CourtListener has no docket record for this petition, so the provisioned
   snapshot (2026-07-16, one day before this run) remained the freshest docket
   source. No further MCP calls made.

## Web searches

None.
