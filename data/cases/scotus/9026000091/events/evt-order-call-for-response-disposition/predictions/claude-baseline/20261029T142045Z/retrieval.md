# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`:
  refused (usage error: `modern` is not an era token). No reads.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`:
  returned 5 recent SCOTUS grants (none on point).
  `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
- WebFetch of the supremecourt.gov docket page for No. 26-91: entries matching the
  snapshot, plus Oct 2 and Oct 5, 2026 entries (the respondent's motion to extend
  the response deadline to Nov 9, 2026, which was granted). No disposition.
- Read the committed `metrics/statpack.md` (base rates).
- No CourtListener MCP calls.
