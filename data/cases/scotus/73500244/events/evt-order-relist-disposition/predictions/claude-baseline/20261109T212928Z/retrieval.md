# Retrieval

- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage message only (no `--era`/`--limit` combo accepted as typed); no rows.
- `uv run fedcourts query --docket-number 25-7371`: usage message (needed `--court`); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5`: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`. Returned recent granted SCOTUS rows; general context only.
- `uv run fedcourts query --court scotus --docket-number 25-7371`: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`. Returned the McMichael v. United States row.
- WebFetch, supremecourt.gov docket 25-7371 (McMichael): petition denied 10/19/2026 after the 10/16 conference.
- WebFetch, supremecourt.gov docket 25-1342 (this case): matches the snapshot; last entry is the 11/9 distribution for 11/13; no disposition.
- `metrics/statpack.md`: relist-count, amicus and salience-band sections.
