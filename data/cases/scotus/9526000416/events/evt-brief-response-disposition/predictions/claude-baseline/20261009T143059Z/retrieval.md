# Retrieval log

Mode: forward. Retrieval beyond the provisioned inputs was unrestricted; I did
not seek and did not find any disposition of this application.

## Corpus lookups (`fedcourts query`, through the cell's corpus service)

1. `uv run fedcourts query --court scotus --include-applications --disposition granted --era 2020s --limit 15`
   stderr: `ranged corpus reads: 27 GET(s), 7012352 byte(s)`
   Result: 15 rows, all October 2026 application grants, nearly all same-day
   time-extension grants (26A4xx). No substantive-stay prior surfaced.
2. `uv run fedcourts query --court scotus --include-applications --disposition denied --era 2020s --limit 15`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   Result: 15 rows, a few October 2026 application denials (In re Howard,
   Eubanks v. O'Connor) and October 5 cert denials. Not used as priors.

Base rates: `metrics/statpack.md`, "The interim docket (applications)" section
(pooled strictly-prior substantive rate computed from its Term rows: 31 of 301).

## CourtListener MCP

3. `search` type=docket, q="Kingdom v. Trump", courts cadc/dcd/scotus: 0 results.
4. `search` type=docket, docket_number=25-cv-00691, court dcd: docket 69717615,
   KINGDOM v. TRUMP, assigned to Royce C. Lamberth, filed 2025-03-07.
5. `search` type=docket, docket_number=26-5236, court cadc: docket 73520260,
   Alishea Kingdom v. Donald Trump, filed 2026-06-23.
6. `call_endpoint` docket-entries, docket=73520260, date_filed >= 2026-09-01:
   five entries, including the full text of the September 18, 2026 per curiam
   order denying the stay (Wilkins, Walker, Garcia; Walker dissenting) and the
   September 22 briefing schedule (appellant brief due 2026-11-02, reply due
   2026-12-23).
7. `search` type=opinion, q="Mullin v. Doe", court scotus, filed after
   2026-01-01: one cluster (25-1083, decided 2026-06-25). Checked because
   Judge Walker cited it; it is a TPS case, not a BOP case, so not a topical
   prior.

## Web searches

8. `"Trump v. Kingdom" Supreme Court stay application Bureau of Prisons gender dysphoria 26A416` (extended)
9. `D.C. Circuit denies stay Kingdom v. Trump Bureau of Prisons transgender inmates hormone therapy September 2026 Walker dissent`
10. `Supreme Court emergency docket Trump administration applications granted record 2026 Solicitor General Sauer win rate`
11. `Supreme Court emergency application government stay granted OR denied October 2026 "Trump v." shadow docket order`
12. `scotusblog Amy Howe Kingdom transgender inmates opposition stay "October 8, 2026" ... Bureau of Prisons hormone`
13. `"Mullin v. Doe" Supreme Court 2026 stay Bureau of Prisons transgender inmates housing order`
14. `Supreme Court Mullin v. Doe 2026 transgender inmates Bureau of Prisons stay granted ...` (extended)
15. `Trump v. Orr Supreme Court November 6 2025 passport stay granted 6-3 Jackson dissent "likely to succeed"`

## Web fetches

16. https://www.scotusblog.com/cases/trump-v-kingdom/ — case page; docket
    through October 8, no ruling.
17. https://www.supremecourt.gov/docket/docketfiles/html/public/26a416.html —
    the Court's docket; five entries, nothing after October 8.
18. https://www.brennancenter.org/our-work/research-reports/supreme-court-shadow-docket-tracker-challenges-trump-administration
    — tracker as of September 29, 2026: 32 decisions, 24 at least partly for
    the administration, 8 against, this application listed as pending.
19. https://www.scotusblog.com/case-files/emergency/emergency-docket-2025/ —
    interim docket list; the fetch summary mis-coded at least one outcome
    (League of Women Voters), so I relied on the Brennan tracker and the
    application's own citations for recent outcomes.
20. https://www.lawcommentary.com/articles/trump-supreme-court-transgender-health-care-federal-prisons
    — commentary on the application and the D.C. Circuit denial.
21. https://www.supremecourt.gov/DocketPDF/26/26A416/428868/20261008145929279_2026.10.08%20Respondents%20Opposition%20to%20Stay%20Application%20-%20Trump%20v.%20Kingdom%2026A416.pdf
    — the respondents' opposition (52 pages); the fetch tool could not read
    the PDF, so I extracted its text locally with pypdf and read it in full.

Nothing under `data/qp-topics/` was read.
