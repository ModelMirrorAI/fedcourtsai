# Retrieval log

Beyond the provisioned inputs (snapshot, event, context, and the three
`record/documents/` texts) I consulted:

## Committed base rates

- `metrics/statpack.md`, "The merits docket (granted cases)" — pooled the
  per-Term disturbed rates over grant Terms 2015–2024 (rows 2017–2024 are all
  the pack holds): 359/515 = 69.7%, `excluded` count published (67), pool
  clears the 30-parsed floor.

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "605 U.S. 168" --limit 5`
  → no rows.
  stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  stderr note: citations filter — 161 of 590339 rows in scope (scotus) carry
  citation data; empty result usually means missing data, not no match.

## CourtListener MCP

- One attempted call: `search` (type=o, court=ca9, q="Prutehi Litekyan Air
  Force") for the Ninth Circuit opinion metadata → **HTTP 429 rate limit**
  (shared 1400/day quota exhausted, ~89 minutes to reset). No retry; no live
  CourtListener data informed this cell. The Ninth Circuit opinion was read
  instead from the cert petition's appendix in the provisioned
  `petition.txt`.

## Web searches

None.
