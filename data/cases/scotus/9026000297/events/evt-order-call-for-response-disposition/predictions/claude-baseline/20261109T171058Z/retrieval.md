# Retrieval log

- `uv run fedcourts query --court scotus --docket-number 22-240` — first attempt without `--court` was refused (usage error asking for `--court`); retried.
  `ranged corpus reads: 18 GET(s), 4718592 byte(s)` — returned *Jim Justice v. Jonathan R.* (round one of this litigation): denied 2022-10-11, distributed once, no response called for.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3` (an earlier attempt with `--era modern` was refused as an invalid era token).
  `ranged corpus reads: 28 GET(s), 7340032 byte(s)` — generic recent grants; not used substantively.
- `metrics/statpack.md` (committed): sal-v8 band table, relist, CVSG and amicus cuts.
- No CourtListener MCP calls; no web searches.
