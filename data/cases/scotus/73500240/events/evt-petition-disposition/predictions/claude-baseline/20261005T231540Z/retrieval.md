# Retrieval log

## Provisioned inputs (read in full)
- `data/cases/scotus/73500240/record/context.json`
- `data/cases/scotus/73500240/record/snapshots/2026-10-05.json`
- `data/cases/scotus/73500240/record/documents/documents.json`, `questions-presented.txt`, `petition.txt` (including Appendix A panel opinion, concurrence, dissent, and Appendix D en banc denial), `brief-in-opposition.txt`
- `data/cases/scotus/73500240/events/evt-petition-disposition/event.yaml`
- `metrics/statpack.md` (modern cert by disposition, by originating circuit, relist-count cut, CVSG cut, salience-band cut, per-Term table, and the sal-v4 segment base rate by salience band)

## Corpus lookups (`fedcourts query`, via the cell's corpus service)
1. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 12`
   stderr: `ranged corpus reads: 785 GET(s), 205520896 byte(s)` — returned 0 rows (the label is a forward convention; no 2020s rows carry it).
2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 8`
   stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)` — returned 8 recent GVR rows, none on qualified immunity or excessive force; not used beyond confirming the sparse coverage.

## CourtListener MCP lookups
1. `search` (type opinion, court ca5, q "Ramirez Granado qualified immunity", filed after 2025-06-01) — located *Ramirez v. Granado*, No. 24-10755, cluster 10766659 (filed 2025-12-30). Not read on CourtListener; the petition appendix carries the opinion.
2. `search` (type opinion, court scotus, q "Zorn v. Linton qualified immunity", filed after 2025-10-01) — located *Zorn v. Linton*, No. 25-297, cluster 10813527 (decided 2026-03-23).
3. `get_endpoint_item` clusters/10813527 — resolved sub-opinion 11280281.
4. `read_document` opinion 11280281, chunks 0, 1, 2, 6 (7000 chars each) — the per curiam and the opening and close of Justice Sotomayor's dissent, joined by Justices Kagan and Jackson.

## Web searches
None.

## Not retrieved
This petition's own Supreme Court docket (No. 25-1338) on CourtListener or supremecourt.gov, any order list, and anything about its disposition. Nothing under `data/qp-topics/` was read.
