# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-20.json`, `petition.txt`,
`questions-presented.txt`, `documents.json`, `record/context.json`) and the
committed `metrics/statpack.md`:

- `fedcourts query --court scotus --citation "500 U.S. 173" --limit 3` —
  returned no rows.
  stderr: `ranged corpus reads: 1335 GET(s), 349962240 byte(s)` and a `note:`
  line reporting the citation-coverage gap (159 of 590419 scotus rows carry
  citation data). Not retried, per the sparse-filter guidance.

No CourtListener MCP calls and no web searches were made. Background context on
the 2025 emergency-docket grant-termination cases (Department of Education v.
California; NIH v. APHA) is from general legal knowledge predating the
snapshot, not retrieval.
