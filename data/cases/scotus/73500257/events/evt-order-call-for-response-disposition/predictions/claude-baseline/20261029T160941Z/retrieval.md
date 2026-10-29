# Retrieval log

- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5` → usage output (rejected flags); no rows.
- `uv run fedcourts query --court scotus --citation "595 U.S. 1" --limit 3` → `ranged corpus reads: 10 GET(s), 2621440 byte(s)`; empty, with a note that only 200 SCOTUS rows carry citations.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5` → `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; 5 recent GVR rows, none relevant to QI. Not relied on.
- WebFetch of the supremecourt.gov docket page for 25-1355 (forward mode) → entries through October 21, 2026: extension granted to October 5, BIO filed October 5, reply October 19, distributed for the November 6, 2026 conference. No disposition.
- Committed `metrics/statpack.md` read for base rates.
- No CourtListener MCP calls.
