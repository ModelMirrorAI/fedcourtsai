# Retrieval log

Beyond the provisioned inputs (snapshot `2026-10-04.json`, `context.json`, `documents/petition.txt`, `documents/questions-presented.txt`, `documents.json`) and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
  Returned eight recent granted priors (distribution counts 0 to 2, originating courts ca1, ca2, ca6, ca8, cadc). Used only as a sanity check that recent grants are counseled petitions with legal questions, not pro se error-correction petitions; no single prior drove the number.

## CourtListener MCP

1. `search` (type opinion, court ca5, case name "Scroggins v. City of Shreveport", filed after 2025-01-01). One hit: cluster 10705997, docket 24-30777, filed 2025-10-17, status Published.
2. `read_document` (opinion id 11172584). Read the full per curiam majority and Judge Dennis's dissent. This predates the petition and is the decision under review, so it is pre-decision material.

No web searches. No lookup of this case's Supreme Court docket, order lists, or any post-snapshot material about it.
