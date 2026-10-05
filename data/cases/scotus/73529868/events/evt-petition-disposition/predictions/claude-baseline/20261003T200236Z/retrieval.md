# Retrieval log — claude-baseline, scotus/73529868, evt-petition-disposition, run 20261003T200236Z

## Corpus (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12` — `ranged corpus reads: 17 GET(s), 4390912 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --limit 12` — `ranged corpus reads: 0 GET(s), 0 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --limit 60` (filtered locally for government-immigration captions) — `ranged corpus reads: 0 GET(s), 0 byte(s)`
4. `uv run fedcourts query --court scotus --era 2020s --limit 200` (same local filter; looking for companion petitions on § 1225(b)(2)(A)) — `ranged corpus reads: 29 GET(s), 7602176 byte(s)`. Found DHS v. D.V.D. (26-426, granted 2026-09-29) and other recent SG matters; no companion detention petition surfaced in the corpus rows.
5. `uv run fedcourts paths --court scotus --docket 73529868 --event evt-petition-disposition --role predictor`
6. Committed `metrics/statpack.md`: modern-cert disposition, originating-circuit, relist-count, CVSG, salience-band sections and the per-Term "Segment base rate by salience band (sal-v4)" table; `metrics/statpack.json` key listing only.

## CourtListener MCP

1. `search` (opinions, ca6, "Lopez-Campos Putra detention", filed after 2025-06-01) — 0 results
2. `search` (opinions, circuit courts, § 1225(b)(2) / § 1226(a) terms, filed after 2025-07-01) — 0 results
3. `search` (dockets, scotus + ca6, "Lopez-Campos") — 18 results; identified ca6 docket 71782032 (25-1965) and the consolidated appeals 25-1969/1978/1982
4. `search` (opinions, ca6, "Raycraft", filed after 2026-01-01) — 1 result: cluster 10857213 / opinion 11324612, *Lopez-Campos v. Raycraft*, decided 2026-05-11, published
5. `search` (opinions, circuits, "Yajure Hurtado", after 2025-09-01) — 0 results
6. `search` (opinions, circuits, "1225(b)(2)(A)" detention "without inspection" bond) — 0 results
7. `search` (opinions, cadc, § 1225(b)(2) applicant for admission, after 2026-06-01) — 0 results
8. `get_endpoint_item` (dockets, 71782032) — argued 2026-03-18, terminated 2026-05-11, nature of suit 2463 Habeas Corpus – Alien Detainee
9. `read_document` (opinion 11324612, chunks 0–1) — caption, panel, holding, circuit-split paragraph
10. `search_document` (opinion 11324612, "Circuit") — split map: 2d/11th/6th and Judge Lee (7th) vs 5th/8th; Murphy dissent
11. `search_document` (opinion 11324612, "dissent")
12. `search` (opinions, circuits, companion case names / "applicants for admission" "mandatory detention", published, after 2025-10-01) — 0 results
13. `search` (dockets, scotus, ICE / Raycraft / Mullin / "Field Office", after 2026-03-01) — 0 results
14. `search` (dockets, scotus, companion case names, after 2026-01-01) — 0 results
15. `search` (dockets, scotus, Freden / Bondi / Noem / "Homeland Security", after 2026-05-01) — 0 results
16. `search_document` (opinion 11324612, "due process") — freestanding procedural due-process holding, pp. 21–24
17. `search_document` (opinion 11324612, "we AFFIRM")

## Web (forward mode; this case is pending)

1. `WebFetch` supremecourt.gov docket 25-1415 — entries identical to the snapshot; nothing after 2026-09-25
2. `WebFetch` the docketed 2026-09-25 letter PDF (text extracted locally with pypdf) — respondents' counsel, re 25-1415 / 26-104 / 26-43, noting the dismissal of *Genalo v. G.M.* (25-886) and the SG's cert-before-judgment petition *Genalo v. D.C.* (26-379), urging grant on the statutory question only
3. `WebSearch` "Putra v. Lopez-Campos certiorari 25-1415 …" — SCOTUSblog case page, justice.gov petition PDF, CLINIC circuit-split note
4. `WebSearch` "Supreme Court September 2026 long conference grants immigration detention …" — PBS, Washington Times, others reporting the 2026-10-01 grant in *Rhoney v. Barbosa da Cunha*
5. `WebFetch` scotusblog.com/cases/raycraft-v-lopez-campos — status pending, QPs, proceedings
6. `WebFetch` PBS report on the 2026-10-01 grant
7. `WebFetch` cliniclegal.org circuit-split note — HTTP 403, not read
8. `WebSearch` "Rhoney v. Barbosa da Cunha" docket / grant — order list URL, SCOTUSblog case page and news story, SG hold-petition PDF
9. `WebFetch` scotusblog.com 2026-10 story on the grants — *Rhoney* granted; Court declined the suggestion to take *Putra* instead
10. `WebFetch` supremecourt.gov order list 100126zr (text extracted locally) — 26-104 "granted"; 25-1415 not mentioned
11. `WebFetch` scotusblog.com/cases/rhoney-v-barbosa-da-cunha — statutory-only QP; granted 2026-10-01
12. `WebFetch` justice.gov/osg/brief/rhoney-v-barbosa-da-cunha — index page only
13. `WebFetch` justice.gov SG hold petition in *Rhoney* (text extracted locally) — asked the Court to hold *Rhoney* pending *Putra*; Second Circuit reached due process only via avoidance
14. `WebFetch` justice.gov SG petition in *Putra* (text extracted locally) — two QPs; "best vehicle for resolving both issues"; respondents released after district-court rulings

Nothing retrieved concerns this petition's own disposition; the latest item about this docket is the 2026-09-25 letter.
