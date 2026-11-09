# Retrieval

- WebFetch: supremecourt.gov docket 25-1324. The entries match the snapshot through the Nov 9, 2026 distribution for 11/13, with nothing newer.
- WebSearch: "Novotny v. Moore 25-1324 relist sensitive places Supreme Court" returned advocacy coverage (ammoland, SAF) describing the petition and Wolford, with no disposition.
- WebSearch: "Supreme Court sensitive places petition relisted 2026 Koons en banc Third Circuit Schoenthal" showed Koons en banc granted Dec. 2025 and argued Feb. 11, 2026. No decision was reported.
- `uv run fedcourts query --court scotus --docket-number 25-1206` returned the Moore v. Kipke row. `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 3` returned generic GVR priors. `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
- Two earlier query attempts failed on usage errors: `--docket-number` without `--court`, and `--era modern`. Both were reissued as above.
- `uv run fedcourts query --help`
- Read `metrics/statpack.md`: the modern-cert, relist, CVSG, amicus and sal-v8 band sections.
- No CourtListener MCP calls.
