# Retrieval log

- `uv run fedcourts query --docket-number 24-1016` → usage error (needs --court); re-issued below.
- `uv run fedcourts query --court scotus --docket-number 24-1016` → `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. RiseandShine v. PepsiCo row: from ca2, CVSG 2025-10-06, granted 2026-06-29, undecided.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5` → `ranged corpus reads: 29 GET(s), 7602176 byte(s)`. A shape check of recent GVR priors; nothing case-specific.
- WebFetch of the supremecourt.gov docket page for 26-238 (forward mode). It shows entries after the cutoff: response deadline extended to Nov 2, 2026 (Sep 15/16), and amicus briefs from NMPA et al. and Songwriters of North America (Oct 13). No disposition.
- Committed `metrics/statpack.md`: the sal-v4 band table and the relist, CVSG, amicus and circuit cuts.
- No CourtListener MCP calls.
