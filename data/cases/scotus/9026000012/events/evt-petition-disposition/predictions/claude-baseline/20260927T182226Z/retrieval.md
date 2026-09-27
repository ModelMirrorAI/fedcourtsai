# Retrieval log — claude-baseline / 20260927T182226Z

## Corpus tooling

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   `ranged corpus reads: 25 GET(s), 6422528 byte(s)`
   Returned 8 rows, mostly OT2025 substantive emergency applications and two
   OT2025 cert grants unrelated to this subject; not used for the number.
2. `uv run fedcourts query --court scotus --citation '146 S. Ct. 541' --citation '145 S. Ct. 15' --limit 5`
   `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   Empty; printed the `note:` that only 200 SCOTUS rows carry reporter
   citations. Not used.

Base rates: read the committed `metrics/statpack.md` — modern cert by
disposition, by originating circuit, relist-count and CVSG cuts (paid scored
segment), the per-Term table, and the sal-v4 salience-band table (pooled
`elevated` bracketed `reached` over OT2017–OT2025 = 16.9%, n = 3,085).

## CourtListener MCP (5 calls)

1. `search` type=o, court=ca4, q="Association for Education Fairness" Montgomery County Board of Education → 1 hit: the published 2023 opinion, 88 F.4th 495 (No. 23-1068). Not read.
2. `search` type=d, court=scotus, q="Coalition for TJ" OR "Boston Parent Coalition" → 0 hits.
3. `search` type=o, court=ca4, filed_after=2026-01-01, q="Association for Education Fairness" → 0 hits (the 2/3/2026 unpublished per curiam is not indexed; I relied on the petition and BIO's description of it).
4. `search` type=d, court=scotus, filed_after=2023-06-01, q on Fairfax County School Board / School Committee / School District of Philadelphia / Sargent → 0 hits.
5. `search` type=o, court=ca3, filed_after=2025-06-01, q="Sargent" "School District of Philadelphia" Arlington Heights → 1 hit: Sherice Sargent v. School District of Philadelphia, No. 24-3112, filed 2026-02-02, published. Not read; the briefs' characterization was used.

## Web fetches (3), all forward-mode, none touching this case's disposition

1. Petitioner's reply brief, `https://www.supremecourt.gov/DocketPDF/26/26-12/423741/20260910113732917_AFEF%20SCOTUS%20Reply.pdf` — the fetch tool could not extract text, so the saved PDF was text-extracted locally with `pdftotext` and read in full.
2. Supreme Court docket page for No. 23-170 (Coalition for TJ v. Fairfax County School Board) — distribution history (7 distributions), 12 cert-stage amici, denied 2/20/2024 with Alito dissent joined by Thomas.
3. Supreme Court docket page for No. 23-1137 (Boston Parent Coalition v. School Committee for the City of Boston) — distribution history (8 distributions), 8 cert-stage amici, denied 12/9/2024 with Gorsuch statement and Alito dissent joined by Thomas.

No search surfaced any disposition of No. 26-12 itself. Nothing under
`data/qp-topics/` was read.
