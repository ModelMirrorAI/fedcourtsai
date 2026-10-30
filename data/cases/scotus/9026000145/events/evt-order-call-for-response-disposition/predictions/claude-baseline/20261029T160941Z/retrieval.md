# Retrieval log

Corpus (via cell service):
1. `uv run fedcourts query --docket-number 25-1223` — refused: usage error (`--docket-number needs --court`). No read line.
2. `uv run fedcourts query --court scotus --disposition gvr --era roberts --limit 5` — refused: unknown era token. No read line.
3. `uv run fedcourts query --court scotus --docket-number 25-1223 --include-open` —
   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned *Montoya Palacios v. Liggins*
   (granted 2026-06-29, from CA4, 2 distributions; amici include counsel for Michelin).
4. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5` —
   `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. Five recent GVR rows; used only as general shape.

Committed base rates: `metrics/statpack.md` (salience-band table, sal-v4).

No CourtListener MCP calls and no web searches.
