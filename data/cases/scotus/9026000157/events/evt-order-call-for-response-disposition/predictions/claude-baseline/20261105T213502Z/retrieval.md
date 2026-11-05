# Retrieval log

- `uv run fedcourts query --docket-number 25-849` / `--docket-number 26-466` (without `--court`): usage error. They needed `--court`.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (unknown era).
- `uv run fedcourts query --court scotus --docket-number 25-849`: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`. USCCB v. O'Connell: denied 2026-05-26 after 4 distributions. Run again later for its disposition fields (warm cache).
- `uv run fedcourts query --court scotus --docket-number 26-466`: `ranged corpus reads: 0 GET(s), 0 byte(s)`. Christian v. Lutheran Church–Missouri Synod: filed 2026-10-07, pending, 0 distributions, from CA5.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3`: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`. A general look at the recent grants population; not decisive.
- WebSearch (standard): "Supreme Court certiorari church autonomy "neutral principles" petition 2026 Lutheran Church Missouri Synod v. Christian". It surfaced the No. 26-466 petition and extension application, this case's petition PDF, and O'Connell materials. Nothing about this case's disposition.
- Read `metrics/statpack.md` (relist, CVSG, amicus and salience-band sections).
- No CourtListener MCP calls.
