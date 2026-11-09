# Retrieval log

- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-310.html: the live docket. Same entries as the snapshot; nothing after Oct 22, 2026 "Response Requested."
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-156.html: Springfield R-12 Sch. Dist. v. Henderson (cited in the petition, n.10). Petition DENIED Oct 5, 2026.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage/no rows (flag combination printed the help text). No ranged-read line was captured from that attempt.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. These were recent granted priors (unrelated subject matter) and were used only as context.
- `uv run fedcourts query --court scotus --docket-number 26-156`: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`. Returned the Henderson row.
- `uv run fedcourts query --help` (usage only).
- Read the committed `metrics/statpack.md` (band table, relist/CVSG/amicus cuts).
- No CourtListener MCP calls and no web searches.
