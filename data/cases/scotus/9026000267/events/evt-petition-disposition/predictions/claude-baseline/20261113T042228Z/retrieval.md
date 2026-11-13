# Retrieval log

- `uv run fedcourts query --help` — read the flag list.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5` — usage error (`modern` is not an era value); printed help, no rows.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5` — 5 recent granted rows, none on ERISA; no use beyond confirming the surface. stderr: `ranged corpus reads: 33 GET(s), 8585216 byte(s)`.
- `metrics/statpack.md` — modern cert dispositions, originating circuit, relist, CVSG, amicus-count and salience-band cuts, per-Term band table.
- Web search (standard): "Trauernicht v. Genworth Fourth Circuit 2026 ERISA 502(a)(2) individual accounts circuit split certiorari" — returned law-firm and trade-press summaries of the Fourth Circuit's 10 March 2026 decision reversing Rule 23(b)(1) class certification; nothing on this petition's disposition and no forecast of it.
- No CourtListener MCP calls. No fetch of the Court's live docket.
