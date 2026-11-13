# Retrieval log

Beyond the provisioned inputs and `metrics/statpack.md` (relist, CVSG, amicus, salience-band and per-Term sections):

1. `uv run fedcourts query --help` — read the flags.
2. `uv run fedcourts query --court scotus --docket-number 26-267` — returned this docket's own open row (no disposition; distribution_count 1). stderr: `ranged corpus reads: 21 GET(s), 5439488 byte(s)`.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5` — five recent granted rows (26A560, 25-1408, 26A512, 26-12, 26-204), none on ERISA; not used. stderr: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`.
4. WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-267.html` — live docket. Entries after my baseline: Oct 8 motion to extend the response time; Oct 9 extension granted to Dec 2, 2026; Nov 2 brief amici curiae of The American Benefits Council et al. filed. No disposition.
5. WebSearch (standard): "Trauernicht v. Genworth Fourth Circuit 2026 ERISA 502(a)(2) defined contribution individual account class certification circuit split certiorari" — law-firm summaries confirming the Fourth Circuit's March 2026 decision (169 F.4th 459) vacating a Rule 23(b)(1) class and treating these claims as individualized. Nothing on certiorari in that case; no forecast of this case surfaced.

No CourtListener MCP calls.
