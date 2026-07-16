# Retrieval

## Corpus and base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. Relevant estimates were a 5.36% grant rate for paid Term 2025 petitions, a 3.0% grant rate for modern cert petitions from the Ninth Circuit, a 0.8% grant rate for petitions with zero relists, and a 3.0% rate with no CVSG.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation 'Moore v. Harper' --citation 'North Carolina v. Covington' --limit 8`. It failed before producing results because the ranged corpus remote's hostname could not be resolved. No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search for `racial gerrymandering mootness remedial map Covington Moore v. Harper`, Supreme Court, filed before January 23, 2026: no results.
- Opinion search for *Moore v. Harper*: located 600 U.S. 1 (2023).
- Opinion search for *North Carolina v. Covington*: located 585 U.S. 969 (2018) and its opinion records.
- Opinions endpoint lookup for opinion 9886704: consulted the relevant *Covington* mootness discussion, including its holding that alleged continued racial segregation in remedial districts kept the claims live.
- Opinion search for *Garcia v. Hobbs* in the Ninth Circuit on August 27, 2025: no results.
- Opinion search for `Garcia Hobbs mootness LD 14 LD 15` in the Ninth Circuit, 2025 through January 23, 2026: no results.
- Opinion citation search for `2025 WL 2466997`: no results.
- Opinion search for *Louisiana v. Callais*, Supreme Court, through July 16, 2026: located the April 29, 2026 decision and opinion record 11317641.
- Opinions endpoint lookup for opinion 11317641: consulted the syllabus and holding that Section 2 did not require Louisiana's additional majority-minority district and therefore supplied no compelling interest for the race-based map.
- Opinion search for *Palmer v. Hobbs* in the Ninth Circuit on August 27, 2025: no results.

No web searches were used.
