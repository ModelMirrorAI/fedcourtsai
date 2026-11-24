The corpus service was queried only for the lead case and its earlier emergency proceeding. Both commands used `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`.

- `uv run fedcourts query --court scotus --docket-number 26-426` returned *Department of Homeland Security v. D. V. D.*, granted September 29, 2026, with a November 16 merits-brief entry. Stderr reported `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
- `uv run fedcourts query --court scotus --docket-number 24A1153` returned the earlier *DHS v. D.V.D.* application, granted June 23, 2025. Stderr reported `ranged corpus reads: 1 GET(s), 262144 byte(s)`.

The following lookups used CourtListener MCP.

- `search` for opinions in ca1, docket 26-1212, filed before September 29, 2026, returned the September 18 First Circuit opinion in *D.V.D.*, cluster 10976939, opinion 11444581.
- `search_document` for `Ibarra-Perez` in opinion 11444581 returned two passages citing the Ninth Circuit on country designation and the distinction between discretion and legal authority.
- `search_document` for `1252(f)(1)` in the same opinion returned eight passages addressing class-wide declaratory relief and vacatur.

Local references included `metrics/statpack.md` and the federal-petitioner rows in `metrics/statpack.json`. The first local `uv run fedcourts paths` attempt encountered a read-only default cache. The retry with a writable temporary cache and the existing environment resolved the cell paths. Two local `fedcourts query --help` invocations displayed the filter documentation.
