Consulted `metrics/statpack.md` for the modern cert, originating circuit, paid relist, CVSG, amicus and prior-Term salience tables. The cell’s specific baseline and amicus rates came from the provisioned `context.json`.

- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` returned the available filters and their coverage.
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --citation '596 U.S. 199' --era 2020s --limit 2` returned no rows and a sparse-citation warning. Transfer report: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
- CourtListener opinion search for `Li v. Commissioner of Internal Revenue` in SCOTUS, filed between January 1, 2022 and January 1, 2024, returned no results. I drew no inference about Supreme Court action on that case.
- CourtListener opinion search in SCOTUS for `596 U.S. 199` returned *Boechler v. Commissioner*, No. 20-1472. The nested opinion-ID field was unavailable in that search.
- A second CourtListener search for the same citation returned the syllabus. It concerns equitable tolling of the deadline to seek Tax Court review of a collection determination. [Boechler](https://www.courtlistener.com/opinion/6461474/boechler-v-commissioner/)
- `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --docket-number 20-1472 --limit 1` returned the *Boechler* row, recording a grant and subsequent reversal. Transfer report: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
