# Retrieval log

Corpus (`fedcourts query`):

1. `uv run fedcourts query --docket-number 26-104` (also `25-1415`, `26-43`) — refused: usage error, `--docket-number needs --court`. Nothing returned.
2. `uv run fedcourts query --court scotus --disposition gvr --era modern` — refused: `Unknown era 'modern'`. Nothing returned.
3. `uv run fedcourts query --court scotus --docket-number 26-104` — returned the lead case's row (*Rhoney v. Barbosa da Cunha*, cert granted 2026-10-01, from ca2, one distribution, no decision). stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
4. `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5` — five recent GVR rows, none on this question; not used. stderr: `ranged corpus reads: 30 GET(s), 7733248 byte(s)`.
5. `uv run fedcourts query --help` — read the interface.

Base rates: `metrics/statpack.md` (salience band table, relist, CVSG and amicus cuts); `record/context.json` frozen `cert_anchor` and `cert_amicus_line`.

Web search (1): "Rhoney v. Barbosa da Cunha Supreme Court 26-104 certiorari granted 1225(b)(2)(A) argument" — result summary confirmed the October 1, 2026 grant, the question presented, the Second Circuit origin, and reported (from the respondent's counsel's case page) that argument is expected in late February or early March 2027. No result claimed a disposition of No. 26-572, and no forecast of either case surfaced. I opened none of the result pages.

CourtListener MCP: not used.

Also read: `data/cases/scotus/9026000572/summaries/2026-11-22.md` (a pipeline summary of the docket; no forecast in it).
