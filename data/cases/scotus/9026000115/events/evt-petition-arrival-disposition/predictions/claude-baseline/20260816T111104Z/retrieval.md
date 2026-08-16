# Retrieval log

Beyond the provisioned inputs (snapshot, `petition.txt`,
`questions-presented.txt`, `documents.json`, `record/context.json`) and the
committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --citation "600 U.S. 447" --limit 8`
  — intended as a search for priors citing Groff v. DeJoy; returned **zero
  rows** (the `--citation` filter matches a case's *own* reporter cites, not a
  citing-cases graph, as its `note:` output states).
  - `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`

## CourtListener MCP

- `search` (opinions, ca4, q=`Dodson "Lutheran Village"`) — 0 results.
- `search` (opinions, all courts, q=`Dodson "Millers Grant"`) — 0 results
  (consistent with the decision below being unpublished; the opinion text is
  in the petition's appendix anyway).
- `search` (dockets, ca4, docket 25-1696) — 1 result: *Cara Liberto Dodson v.
  The Lutheran Village at Millers Grant, Inc.*, filed 2025-06-20. Confirms
  the appeal docket; no outcome-bearing material for the pending petition.

## Web

None.
