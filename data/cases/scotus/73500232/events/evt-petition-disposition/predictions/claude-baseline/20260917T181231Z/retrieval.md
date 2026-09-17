# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-17.json`, `context.json`, `event.yaml`, `documents.json`, `questions-presented.txt`, `petition.txt`) and the committed `metrics/statpack.md`:

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned eight recent granted rows — four substantive applications (People Not Politicians v. Onder; NRCC v. Brown; National Park Service v. National Trust for Historic Preservation; a fourth with 13 amicus briefs) and four counseled cert petitions (Jouppi v. Alaska; Viramontes v. Cook County; Grant v. Higgins; one more). None is a pro se or Rule 4(a)(5) comparator; used only as a picture of what the segment's grants look like.

## CourtListener MCP lookups

- `search` (type `o`, court `ca3`, q `Mazza "Bank of New York Mellon"`, filed after 2024-01-01) — **failed**: HTTP 429, rate limit exceeded (300/hour), reset in roughly 333 seconds. Not retried. The Third Circuit opinion below (No. 24-2794, May 16, 2025) was therefore not read; its characterization in `reasoning.md` comes from the petition.

## Web searches

None.
