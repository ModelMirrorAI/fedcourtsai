# Retrieval log

Corpus:
- `uv run fedcourts query --court scotus --docket-number 26-589` — returned the companion's row (pending, distribution_count 0, no disposition). stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
- `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 5` — rejected: usage error (`roberts` is not an era token); no rows, no transfer line. Not re-issued.
- `metrics/statpack.md` — "Segment base rate by salience band (sal-v8)" table.

Web (forward mode):
- WebFetch `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-589.html` — live docket of the companion: petition filed 2 Nov 2026; respondent's motion to extend the response time (10 Nov), SG response opposing, reply; extension granted in part to 15 Dec 2026 (12 Nov).
- WebFetch of the government's petition PDF in 26-589 (`.../DocketPDF/26/26-589/431482/20261102131123209_Climate%20United%20Petition.pdf`) — the fetch returned binary; I read the saved PDF with `uv run fedcourts pdf-text` (212 pages): questions presented (Tucker Act; repealed 42 U.S.C. 7434), the alleged Fourth Circuit conflict, and the conclusion (plain request for certiorari).

CourtListener MCP: no calls.
