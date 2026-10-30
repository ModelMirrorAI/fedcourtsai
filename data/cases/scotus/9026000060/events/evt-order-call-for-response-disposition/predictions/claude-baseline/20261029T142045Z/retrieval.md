# Retrieval log

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` —
  printed the usage text instead of rows (the flag set was not accepted). No rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` —
  `ranged corpus reads: 27 GET(s), 7077888 byte(s)`. Returned recent OT2025/OT2026
  grants (e.g. Scanlan v. Coalition for Open Democracy, DOJ v. McNutt,
  FCC v. Brown, U.S. DOGE Service); context only, none on point.
- `uv run fedcourts query --help`, `uv run fedcourts paths …` — local help/path resolution.
- WebFetch `https://www.supremecourt.gov/docket/docketfiles/html/public/26-60.html` —
  the live docket: response-time extension (to Oct 26, 2026), NRA et al. amicus brief
  (Sep 24, 2026), brief in opposition filed Oct 26, 2026; no disposition.
- Committed `metrics/statpack.md` (base rates).
- No CourtListener MCP calls.
