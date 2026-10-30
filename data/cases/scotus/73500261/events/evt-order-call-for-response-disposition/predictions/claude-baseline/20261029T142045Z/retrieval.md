# Retrieval log

- `uv run fedcourts query --help`: usage only.
- `uv run fedcourts query --court scotus --docket-number 26-257`: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`. Nathan v. Alamo Heights: filed 2026-08-27 (corpus date), distribution_count 0, no disposition, last_live_polled 2026-10-25.
- `uv run fedcourts query --court scotus --docket-number 25-1360`: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. This case's own row: distribution_count 1, no disposition, last_live_polled 2026-10-26.
- WebSearch "Nathan v. Alamo Heights petition for certiorari Supreme Court Ten Commandments 2026": ACLU/SCOTUSblog/Constitution Center pages and supremecourt.gov PDFs (the 26-257 petition, an amicus brief in 26-257, the 25-1360 BIO). Used for background: Nathan was a 9–8 en banc decision, and the petition was filed 8/17/2026. No disposition claimed.
- WebFetch of the supremecourt.gov docket for 25-1360: response extensions (to 9/28, then 10/19); BIO filed 10/19/2026; no disposition.
- WebFetch of the supremecourt.gov docket for 26-257: petition filed 8/17/2026; amicus brief 9/28; response extended to 11/10/2026; no disposition.
- Read `metrics/statpack.md` (salience-band table, relist, CVSG and amicus cuts).
- No CourtListener MCP calls.
