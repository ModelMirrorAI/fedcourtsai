# Retrieval
- WebFetch supremecourt.gov docket 25-944 (Robinhood v. Sodha): CVSG 6/1/2026, SG brief 10/7/2026, distributed for 11/6 and then 11/13.
- WebFetch supremecourt.gov docket 25-1376 (this case): matches the snapshot. No entries after 11/9.
- WebSearch "Robinhood v. Sodha Solicitor General brief Section 11 Item 303 recommends": the snippet says the SG recommends granting Robinhood's first question. I did not open the brief itself.
- `uv run fedcourts query --court scotus --docket-number 25-944 --include-open` printed `ranged corpus reads: 18 GET(s), 4718592 byte(s)` and returned the Robinhood row (counsel only read).
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 3` printed `ranged corpus reads: 19 GET(s), 4980736 byte(s)`. It returned generic GVR priors and did not inform the number.
- Two earlier `fedcourts query` attempts failed with usage errors (`--disposition gvr --era modern`, an invalid era token; `--docket-number 25-944` without `--court`). Neither returned rows.
- Statpack: the `metrics/statpack.md` relist and CVSG cuts.
