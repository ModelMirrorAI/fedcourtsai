# Retrieval log

Provisioned inputs read: `record/snapshots/2026-09-15.json`, `record/context.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, the event's `event.yaml`, `metrics/statpack.md`, `schemas/prediction.schema.json`, `AGENTS.md`, `.github/prompts/predict.md`.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --corpus-backend service`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
  Returned recent substantive emergency applications (e.g. 26A326, 26A274) ahead of any cert prior; not used for the number.

## CourtListener MCP lookups (5 calls)

1. `search` type=o, q="Zorn v. Linton", court=scotus, filed_after=2025-10-01 — located No. 25-297, decided 2026-03-23 (cluster 10813527).
2. `search` type=o, same query with `opinions`/`posture`/`syllabus` fields — obtained opinion id 11280281.
3. `search` type=o, q="qualified immunity" "per curiam" "clearly established", court=scotus, filed_after=2022-10-01, newest first — *Zorn v. Linton* was the only recent qualified-immunity per curiam surfaced; other hits were unrelated.
4. `read_document` opinion_id=11280281, chunk 0 of 4 (14,000 chars) — read the per curiam's facts and Part II (summary reversal of CA2's denial of qualified immunity to an officer removing a passively resisting protester).
5. `search` type=d, court=scotus, docket_number=25-1314 — no CourtListener docket for this case (0 results).

## Web fetch (forward mode, this case's own public filing)

- `curl` of the brief in opposition linked from the snapshot's September 14, 2026 docket entry:
  `https://www.supremecourt.gov/DocketPDF/25/25-1314/424147/20260914154313299_Gomez%20v.%20Saccoccio%20BIO%2025-1314.pdf` (19 pages), text extracted locally with pypdf and read in full. The document was on the docket at snapshot time but not among the provisioned documents.

No other web searches. Nothing under `data/qp-topics/` was read.
