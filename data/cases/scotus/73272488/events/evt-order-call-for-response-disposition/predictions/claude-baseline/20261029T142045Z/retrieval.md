# Retrieval log

- WebFetch https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-1236.html — the live docket for this case. Showed three response extensions, the BIO (9 Oct 2026), the reply (23 Oct 2026), and a distribution for conference 11/13/2026. No disposition.
- WebFetch https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-6344.html — Tovar v. United States (the same question, CA11). Response requested; petition denied 18 May 2026.
- WebFetch on the 25-1236 docket page again, to get the BIO and reply PDF links.
- WebFetch https://www.supremecourt.gov/DocketPDF/25/25-1236/429127/20261009152911466_Abrams_Opp_25-1236-final.pdf — the summarizer could not read the PDF. I extracted the saved PDF's text locally with pypdf (22 pages) and read it in full.
- Read attempt on the same PDF failed (pdftoppm not installed).
- `uv run fedcourts query --court scotus --docket-number 25-6344` → `ranged corpus reads: 12 GET(s), 3145728 byte(s)`; confirmed Tovar denied 2026-05-18, ca11, distribution_count 2.
- `uv run fedcourts query --docket-number 25-6344` (without --court) → usage error, no read.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` → usage error (bad era token), no read.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` → `ranged corpus reads: 25 GET(s), 6553600 byte(s)`; generic recent grants, not used.
- `metrics/statpack.md` (committed) for base rates.
- No CourtListener MCP calls.
