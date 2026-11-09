# Retrieval

- `uv run fedcourts query --court scotus --docket-number 25-7371` → McMichael v. United States (same QP, CA11, from *Bryan*): denied 2026-10-19, one distribution (10/16).
  `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
- `uv run fedcourts query --court scotus --disposition granted --era modern` → usage hint only (no rows used).
- `uv run fedcourts query --help`.
- WebFetch supremecourt.gov docket 25-7371 → confirmed: BIO 9/11, distributed for 10/16, petition denied 10/19.
- WebFetch supremecourt.gov docket 25-1342 → same as snapshot; latest entry 11/9 distributed for the 11/13 conference, no disposition.
- Read `metrics/statpack.md` (salience band table sal-v8, relist-count cut, CVSG cut).
- No CourtListener MCP calls.
