# Retrieval log

- `uv run fedcourts query --court scotus --disposition denied --era modern --include-applications --limit 5` → usage error (printed help; no rows).
- `uv run fedcourts query --court scotus --disposition denied --include-applications --limit 5` → `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Recent OT2026 substantive applications (Guardado, Lopez Jaime, Taylor); used for shape only.
- `uv run fedcourts query --court scotus --docket-number 26A657` → `ranged corpus reads: 17 GET(s), 4325376 byte(s)`. This docket's own corpus row: substantive, pro se, no disposition.
- Statpack: `metrics/statpack.md` interim section and `metrics/statpack.json` `interim.terms` finer counts (local files).
- WebFetch supremecourt.gov docket 26A657 → only the Nov 2, 2026 submission entry; lower court CA4 26-2406.
- CourtListener MCP `search`: first call failed on argument validation (the schema was not loaded). Retried as a docket search with party_name=Schultz, q=McCarthy, filed_after 2025-06-01 → *Schultz v. McCarthy* dockets in E.D. Va. bankruptcy court (25-01061) and E.D. Va. district court (several 2026 civil numbers).
