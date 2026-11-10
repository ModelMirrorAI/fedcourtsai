# Retrieval log
- WebFetch: supremecourt.gov docket page for 26-292. It matched the snapshot entries through 11/9 (distributed for 11/13) and lists no respondent counsel.
- WebSearch (standard): "Havlish Taliban Supreme Court petition Da Afghanistan Bank TRIA 2026". It returned background (Second Circuit opinion, TLB blog on the en banc denial). I found no claim of a disposition.
- WebSearch (standard): "\"26-292\" Havlish supplemental brief Supreme Court Taliban relist". It showed that the supplemental brief responds to the Afghan mission's amicus brief. No disposition was reported.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`: usage error (no `--era modern` value accepted / help printed). I re-issued it without `--era`.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` → `ranged corpus reads: 31 GET(s), 8126464 byte(s)`. It returned recent unrelated grants, which served only as a sanity check.
- `uv run fedcourts query --help` (help text only).
- Statpack read: `metrics/statpack.md` (modern cert, relist, CVSG, amicus and sal-v8 band tables).
