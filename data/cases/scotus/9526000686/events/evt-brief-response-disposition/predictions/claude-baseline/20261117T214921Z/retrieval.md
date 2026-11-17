# Retrieval log

1. `uv run fedcourts query --help` (interface help).
2. `uv run fedcourts query --court scotus --docket-number 26-6154`: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. Returned the linked cert petition's row (Overton v. Florida, capital, filed 2026-11-14, no distribution, no disposition).
3. `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 5`: usage error (`modern` is not an era token); no rows.
4. `uv run fedcourts query --court scotus --disposition denied --era 2020s --include-applications --limit 8`: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`. Returned eight unrelated cert denials dated 2026-11-16; not used.
5. Read committed `metrics/statpack.md`, interim-docket section and applicant-class table.

No CourtListener MCP calls and no web searches.
