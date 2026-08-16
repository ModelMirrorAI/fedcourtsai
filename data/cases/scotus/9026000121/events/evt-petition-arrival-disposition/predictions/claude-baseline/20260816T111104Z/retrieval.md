# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`,
`record/context.json`, `record/documents/petition.txt`,
`record/documents/questions-presented.txt`, `record/documents/documents.json`)
and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --citation "556 U.S. 868" --limit 8`
   — attempted to pull priors sharing the Caperton citation. Returned **no
   rows**; stderr:

   ```
   ranged corpus reads: 1329 GET(s), 348389376 byte(s)
   note: citations filter: 161 of 590339 rows in scope (scotus) carry citation data, and the column holds a case's OWN reporter cites (not a cases-citing-this-authority graph) — an empty result here usually means missing data, not no match
   ```

   Read as a coverage gap per the note; not retried on other sparse filters.

## CourtListener MCP lookups

None.

## Web searches

None.
