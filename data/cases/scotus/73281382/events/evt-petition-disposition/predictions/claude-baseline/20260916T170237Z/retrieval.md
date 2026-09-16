# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-15.json`, `context.json`, `event.yaml`, `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`, `documents.json`) and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Result: recent granted SCOTUS rows, generically ranked (largely substantive applications and election matters); no knock-and-talk or curtilage priors surfaced. Did not inform the number.

## CourtListener MCP lookups

1. `search` type=docket, court=scotus, q=`"knock and talk" OR "knock-and-talk"`, filed_after 2024-06-01 — 0 results (checking for companion petitions pending alongside this one).
2. `search` type=opinion, court=scotus, q=`"knock and talk" OR "knock-and-talk" OR Jardines curtilage`, filed_after 2023-01-01 — 1 result: Chatrie v. United States, No. 25-112, decided 2026-06-29. Not a companion case; not opened.

No searches for this case's own docket, disposition, or coverage.

## Web searches

None.
