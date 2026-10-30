# Retrieval log

- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-193.html (companion *Hall v. Fleming*). Returned the full docket: petition 8/11/2026, 15 amicus entries, BIO 10/14, reply 10/26, distributed for 11/13/2026 conference and rescheduled 10/28. No disposition.
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-240.html (this docket). Entries after the snapshot: on 10/21 Virginia moved to extend the response deadline to 12/4, and petitioners responded; on 10/22 the motion was granted in part, extending the deadline to 11/17/2026. No disposition.
- `uv run fedcourts query --court scotus --docket-number 26-193`. stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned the *Hall* row, open and unresolved.
- `uv run fedcourts query --court scotus --citation "540 U.S. 712"`. stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No rows, plus a coverage `note:` that the citations column is sparse.
- Read committed `metrics/statpack.md` for base rates.
- No CourtListener MCP calls.
