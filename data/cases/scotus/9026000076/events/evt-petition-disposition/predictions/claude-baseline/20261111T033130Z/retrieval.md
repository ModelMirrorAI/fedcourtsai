# Retrieval log
- WebFetch https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-76.html: the live docket has no entries after Aug 28, 2026 ("Rescheduled"), matching the snapshot.
- WebSearch "Supreme Court Florida non-unanimous jury death penalty 8-4 petition Jackson v. Florida Hunt v. Florida 2026": returned news of the Florida Supreme Court's decision of Dec 18, 2025 upholding the 8-4 statute in Jackson and Hunt, and Hunt's cert petition PDF. No report of a U.S. Supreme Court disposition.
- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5`: usage error (`modern` is not an era token). No reads.
- `uv run fedcourts query --docket-number 26-78`: usage error (it needs `--court`).
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 3`: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`. Returned generic recent denials, used only as context.
- `uv run fedcourts query --court scotus --docket-number 26-78`: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`. Hunt v. Florida is open, capital, with Fisher as counsel and Waxman for an amicus.
- Read `metrics/statpack.md` (the modern-cert, relist, CVSG, amicus, capital and salience-band sections).
