# Retrieval

- `metrics/statpack.md` — "The merits docket (granted cases)" section (committed file; no corpus transfer).
- CourtListener MCP `search` (type=o, court=ca4, q="Ozurumba") → cluster 10665527, opinion 11132114 (Ozurumba v. Bondi, No. 24-2070, 4th Cir. Sept. 2, 2025).
- CourtListener MCP `read_document` opinion 11132114, chunks 0–4 (majority opinion and opening of the dissent).
- WebSearch: "Supreme Court 25-1343 Ozurumba material support question presented" — returned only coverage of the Fourth Circuit decision (Virginia Lawyers Weekly, Bloomberg Law, Amica Center, FindLaw); no petition text and nothing about this case's disposition.
- No `fedcourts query` / `open-events` calls, so there are no `ranged corpus reads` lines to record.
