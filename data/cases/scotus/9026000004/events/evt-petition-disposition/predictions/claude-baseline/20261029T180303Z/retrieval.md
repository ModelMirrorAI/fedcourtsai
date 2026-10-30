# Retrieval log

- `uv run fedcourts query --docket-number 21-926` — refused (needs `--court`); printed usage text and `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
- `uv run fedcourts query --court scotus --citation "600 U.S. 122"` — empty; note line about sparse citation column.
- `uv run fedcourts query --court scotus --docket-number 21-926` — Cooper Tire & Rubber Co. v. McCall: disposition `denied`, distribution_count 4, no CVSG. `ranged corpus reads: 12 GET(s), 3145728 byte(s)`.
- `uv run fedcourts query --court scotus --docket-number 21-1168` — Mallory v. Norfolk Southern row (context only). `ranged corpus reads: 1 GET(s), 262144 byte(s)`.
- Re-ran the 21-926 query to extract fields (stderr suppressed, so no read line captured).
- Read the committed `metrics/statpack.md` (relist, CVSG, amicus, band, and per-Term sal-v4 sections).

No CourtListener MCP calls and no web searches.
