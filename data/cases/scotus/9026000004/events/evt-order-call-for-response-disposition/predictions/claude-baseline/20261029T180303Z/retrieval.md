# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 21-926` —
  `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned *Cooper Tire &
  Rubber Co. v. McCall*: denied 2023-06-30, distribution_count 4, no CVSG.
- `uv run fedcourts query --court scotus --citation "600 U.S. 122"` —
  `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. Empty, with the
  citations-coverage note.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` —
  `ranged corpus reads: 22 GET(s), 5767168 byte(s)`. Five recent grants; not
  topically related, not used.
- Committed `metrics/statpack.md` (base rates).

No CourtListener MCP or web searches.
