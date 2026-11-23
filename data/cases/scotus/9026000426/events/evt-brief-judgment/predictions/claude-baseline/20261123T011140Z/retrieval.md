# Retrieval log

- `metrics/statpack.md`: read "The merits docket (granted cases)" and "Per-Justice merits votes" sections.
- `uv run fedcourts query --court scotus --disposition granted --era modern`: usage error (unknown era); nothing returned.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`: returned 8 recent granted SCOTUS rows (mostly pending federal-petitioner cases); `ranged corpus reads: 37 GET(s), 9568256 byte(s)`. Context only; nothing used in the number.
- `uv run fedcourts query --docket-number 24A1153 --include-applications`: usage error (needs `--court`); not retried.
- No CourtListener MCP calls and no web searches.
