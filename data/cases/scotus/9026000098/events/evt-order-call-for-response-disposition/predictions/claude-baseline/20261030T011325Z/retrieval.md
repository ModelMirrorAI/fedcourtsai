# Retrieval log

- **WebFetch** `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-98.html`: the live docket. It shows two granted extensions of the response deadline (to 26 Oct, then to 25 Nov 2026). There is no disposition.
- **WebSearch** "United States v. Benson Sixth Circuit voter roll NVRA petition certiorari Supreme Court 2026": CRS LSB11456 on the 6th Cir. affirmance (24 June 2026, Civil Rights Act Title III), plus a note that PILF v. Benson cert was denied in March 2026.
- **WebSearch** about Benson rehearing en banc / cert: DOJ sought rehearing en banc in the 6th Cir., and it was denied. There was no information about this case's disposition.
- **Corpus query** `uv run fedcourts query --court scotus --docket-number 25-5872`: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. It returned Jackson v. Benson (an IFP petition, denied 2026-01-12), which was not useful.
- **Corpus query** `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: a usage error (unknown era). I re-issued it.
- **Corpus query** `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`: `ranged corpus reads: 25 GET(s), 6553600 byte(s)`. It returned recent OT2026 grants (e.g., Scanlan v. Coalition for Open Democracy), used for general context only.
- **Statpack**: `metrics/statpack.md`, for the band table and the relist, CVSG, amicus and circuit cuts.
- No CourtListener MCP calls.
