# Retrieval log

## Committed base rates

- Read `metrics/statpack.md`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, and Term tables.
- Read the 2025 Term paid-petition detail in `metrics/statpack.json` (estimated grant rate 5.36%).

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 8`
  - `ranged corpus reads: 25 GET(s), 6488064 byte(s)`
  - Returned eight recent SCOTUS GVR records. They confirmed the current use of the disposition but were not close substantive comparators.

## CourtListener MCP

- Opinion search for `Jules v. Andre Balazs Properties` in SCOTUS after January 1, 2025: found No. 25-83, decided May 14, 2026.
- Opinion search for SCOTUS docket `25-83` after May 1, 2026: identified cluster 10858761 and combined opinion 11326163.
- Opinion endpoint lookup for opinion 11326163: consulted the syllabus and opinion text. The Court unanimously held that jurisdiction over claims stayed under FAA § 3 extends to ensuing §§ 9 and 10 motions.
- Opinion search for `financialright claims Burford` in the Third Circuit during October 2025: no results.
- Opinion search by case name `In re Application of financialright claims GmbH` in the Third Circuit during October 2025: no results.

No web searches were used.
