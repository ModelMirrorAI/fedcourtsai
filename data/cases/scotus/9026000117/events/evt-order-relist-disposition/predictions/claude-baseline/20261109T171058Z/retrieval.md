# Retrieval
- WebFetch: supremecourt.gov docket page for 26-117. It showed the same entries as the snapshot, nothing after the Nov 9, 2026 distribution.
- `uv run fedcourts query --help` (usage).
- `uv run fedcourts query --court scotus --disposition summary-reversal --era modern --limit 5`: returned usage text (bad flag value); no rows.
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`. Returned 5 unrelated GVR priors, which I did not use.
- `uv run fedcourts query --docket-number 25-274` and `--docket-number 26-116`: returned usage text, no rows.
- Read `metrics/statpack.md` (relist-count, CVSG and salience-band tables).
