# Retrieval
- WebFetch supremecourt.gov docket 26-199. The lead HISA petition: all challengers' responses agree it should be granted. Distributed for the 12/4/2026 conference.
- WebFetch supremecourt.gov docket 25-1325 (Oklahoma v. United States, CA6). Rescheduled from the 10/9 conference and distributed for 12/4/2026.
- `uv run fedcourts query --docket-number 26-199` (and 26-201, 25-1325): refused because `--court` was missing. These printed usage text only.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3`: refused because "modern" is not an era token.
- `uv run fedcourts query --court scotus --docket-number 26-199 --include-open` — `ranged corpus reads: 17 GET(s), 4456448 byte(s)`. Returned the open HISA v. NHBPA row.
- `uv run fedcourts query --court scotus --docket-number 25-1325 --include-open` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Returned the Oklahoma v. United States row.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3` — `ranged corpus reads: 19 GET(s), 4980736 byte(s)`. Generic priors, not used.
- Read `metrics/statpack.md`: the relist, CVSG and salience-band sections.
