Consulted the committed `metrics/statpack.md` cert disposition, relist, CVSG, amicus, capital, originating-court, fee-class and salience tables, and the prior-Term rows in `metrics/statpack.json`. The latter contains the sal-v9 alternate series used in the frozen anchor.

The first `uv run fedcourts paths --court scotus --docket 9026000078 --event evt-petition-disposition --role predictor` attempt failed because uv's default cache was read-only. The same command succeeded with `UV_CACHE_DIR=/tmp/uv-cache` and `UV_NO_SYNC=1`. All subsequent CLI calls used those settings. `uv run fedcourts query --help` returned the available filters.

| Corpus command | Returned | Transfer |
| --- | --- | --- |
| `uv run fedcourts query --court scotus --citation '589 U.S. 139' --limit 3` | No rows. The service reported sparse reporter-citation coverage. | `ranged corpus reads: 10 GET(s), 2621440 byte(s)` |
| `uv run fedcourts query --court scotus --docket-number 18-1109 --limit 1` | *McKinney v. Arizona*, certiorari granted June 10, 2019, judgment affirmed in 2020. The legal argument in this forecast comes from the staged briefs. | `ranged corpus reads: 0 GET(s), 0 byte(s)` |
| `uv run fedcourts query --court scotus --docket-number 26-76 --limit 1` | *Michael James Jackson v. Florida*, pending, three distributions, latest conference December 11, 2026. The staged companion snapshot ends with its November 17 reschedule. | `ranged corpus reads: 21 GET(s), 5505024 byte(s)` |
| `uv run fedcourts query --court scotus --docket-number 25-6623 --limit 1` | *Kian v. Florida*, certiorari granted June 15, 2026, merits brief recorded, no merits decision recorded. | `ranged corpus reads: 1 GET(s), 262144 byte(s)` |
