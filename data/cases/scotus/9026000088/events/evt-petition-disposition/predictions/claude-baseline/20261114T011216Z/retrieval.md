# Retrieval log

Beyond the provisioned inputs:

- `metrics/statpack.md` — modern cert dispositions, relist / CVSG / amicus-count / capital / salience-band cuts, and the sal-v8 segment base-rate table.
- `uv run fedcourts query --help` — interface text.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 8` — usage error (unknown era `modern`); no data.
- `uv run fedcourts query --docket-number 23-926 --limit 2` (and 21-890, 24-644) — usage error (`--docket-number needs --court`); no data.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` — `ranged corpus reads: 33 GET(s), 8585216 byte(s)`; five recent granted rows, none on point.
- `uv run fedcourts query --court scotus --docket-number 23-926 --limit 1` — `ranged corpus reads: 18 GET(s), 4718592 byte(s)`; No on E v. Chiu, denied 2024-10-07, distribution_count 2.
- `uv run fedcourts query --court scotus --docket-number 21-890 --limit 1` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`; Gaspee Project v. Mederos, denied 2022-04-25, distribution_count 3.
- `uv run fedcourts query --court scotus --docket-number 24-644 --limit 1` — `ranged corpus reads: 1 GET(s), 262144 byte(s)`; Williams v. Allegheny County (a wrong guess at another analog's number; unrelated, not used).

No CourtListener MCP calls and no web searches.
