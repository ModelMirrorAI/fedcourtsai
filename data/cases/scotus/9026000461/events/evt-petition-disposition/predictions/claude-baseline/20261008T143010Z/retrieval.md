# Retrieval log

Mode: `forward` (context.json). No search surfaced this petition's disposition; none exists.

## Corpus tooling

1. `uv run fedcourts query --court scotus --era modern "reporter privilege ..." --limit 10` — rejected (the command takes no free-text argument); no transfer line.
2. `uv run fedcourts query --court scotus --era 2020s --limit 8` — stderr: `ranged corpus reads: 4 GET(s), 983040 byte(s)`. Returned eight October 2026 resolved rows ranked on shared attributes (stay applications and once-distributed paid denials from the 9/28 conference); subject-unrelated, used only as a sanity read on the current conference cadence.
3. `metrics/statpack.md` — sections "Modern discretionary-cert petitions by disposition", "by originating circuit", "by relist count", "by CVSG status", "by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)". Pooled the baseline band's bracketed `reached` figures over OT2017–OT2025 locally.

## CourtListener MCP

4. `search` (opinions, court cadc, filed after 2025-01-01, "Herridge Chen contempt reporter privilege") — one hit: Yanping Chen v. FBI, No. 24-5050, filed 2025-09-30, cluster 10681709.
5. `call_endpoint` clusters, id 10681709 — sub-opinion 11148296; panel fields empty.
6. `read_document` opinion 11148296, chunks 0–2 (full text, 26,164 chars) — Katsas, J., for a panel with Childs and Edwards; affirmed; declined a federal common-law privilege.
7. `search` (opinions, court cadc, filed after 2025-10-01, "Herridge") — no results (the May 22, 2026 rehearing denial is not indexed as an opinion).

## Web

8. WebSearch: "Catherine Herridge Supreme Court petition certiorari Chen contempt reporter's privilege 2026" — surfaced the stay application No. 25A1448, its July 2, 2026 denial, and the district court's August 2026 pause of the fines.
9. WebSearch: "Herridge v. Chen cert petition questions presented / Branzburg / Clement ... August 2026" — surfaced the stay opposition PDF and coverage of the stay denial; nothing on the petition's text.
10. WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/25a1448.html — stay docket entries, including the July 2 order text ("Justice Kavanaugh would grant the application for stay").
11. WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-461.html — confirms the snapshot: motion 26M17 distributed 9/2 for the 9/28 conference and granted 10/5; petition docketed 10/7, response due 11/6; no other entries.
12. WebFetch https://www.rcfp.org/briefs-comments/chen-v-fbi/ — amicus history (25 media organizations below; stay-stage amicus June 29–30, 2026).
13. WebFetch https://thefederalist.com/2026/09/25/everything-about-the-catherine-herridge-contempt-case-stinks/ — reports only that the petition remains under seal; no content on the questions presented.
14. WebFetch https://deadline.com/2026/07/... and https://deadline.com/2026/06/... — redirected to a paywall (HTTP 402 on follow); not read.
15. WebFetch + local text extraction of the petition PDF https://www.supremecourt.gov/DocketPDF/26/26-461/428714/20261007122400796_Petition.Herridge.pdf — 47 pages, no text layer (0 extractable characters), matching `documents.json`'s `empty_text: true`.
16. Downloaded and extracted (pypdf) the 25A1448 filings: the RCFP amicus brief of June 30, 2026 (text; read in full), Chen's opposition to the stay of July 1, 2026 (48 pages, text; read the introduction, the vehicle argument, and the circuit-split argument), the redacted application and appendix (image-only, no text), and the redacted reply (image-only, no text).

Total: 2 corpus commands, 4 MCP calls, 2 web searches, 9 web fetches or downloads.
