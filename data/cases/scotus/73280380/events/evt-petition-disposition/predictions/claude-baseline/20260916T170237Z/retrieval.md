# Retrieval log

Mode: `forward` (no cutoff; retrieval unrestricted). Provisioned inputs read:
snapshot `2026-09-16.json`, `context.json`, `event.yaml`, `documents.json`,
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`. Base
rates: committed `metrics/statpack.md` (modern cert by disposition, by
circuit, relist/CVSG cuts, per-Term band table under sal-v4).

## Corpus

- `uv run fedcourts query --court scotus --citation "496 U.S. 384" --citation "511 U.S. 659" --citation "498 U.S. 533"`
  stderr: `ranged corpus reads: 1357 GET(s), 355532800 byte(s)`
  Result: no rows; note printed that only 200 of 590880 scotus rows carry
  citation data. Nothing used from it.

## CourtListener MCP

1. `search` (type=o, court=ca9, q="Lake Gates sanctions Parker Olsen Rule 11 1927 rehearing en banc", filed_after 2025-01-01)
   -> one hit: Kari Lake v. Bill Gates, No. 23-16022, order denying rehearing en banc with dissent, filed 2025-08-21 (cluster 10658060, opinion 11124647).
2. `search` (type=d, court=scotus, q="Maricopa County Board of Supervisors sanctions Olsen OR Parker OR Dershowitz", filed_after 2025-06-01)
   -> no results (checking for a companion petition by co-counsel Kurt Olsen).
3. `read_document` (opinion_id 11124647, chunks 0-1 of 9)
   -> confirmed the dissent lineup (VanDyke, joined by Callahan, R. Nelson, Collins, Lee, Bumatay), the panel (Wardlaw, Gould, Bumatay), Judge Desai recused, and the dissent's two grounds. Read only the opening pages; the rest is summarized in the petition's appendix quotations.
4. `search` (type=d, court=scotus, q="\"Olsen\" Gates Maricopa", filed_after 2025-06-01)
   -> no results.

No web searches. Nothing retrieved concerned this petition's own disposition,
which does not yet exist (first conference 9/28/2026).
