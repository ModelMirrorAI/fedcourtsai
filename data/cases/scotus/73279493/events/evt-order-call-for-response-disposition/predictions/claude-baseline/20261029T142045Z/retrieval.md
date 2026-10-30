# Retrieval log

- `uv run fedcourts query --court scotus --era modern --disposition granted --limit 5`
  was rejected as a usage error ("Unknown era 'modern'"). No rows came back.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`:
  `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. It returned five recent
  grants (Scanlan; DOJ v. McNutt; FCC v. Brown; U.S. DOGE Service; one other).
  None bears on § 523(a)(6). Used as general context only.
- `uv run fedcourts query --help`: read the usage text. No corpus read.
- Base rates came from the committed `metrics/statpack.md`.
- No CourtListener MCP calls, no web searches, and no live supremecourt.gov
  docket lookup. I skipped the live docket because this cell runs after the
  likely disposition date, and I wanted to avoid seeing the outcome.
