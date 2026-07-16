# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert dispositions, originating-circuit, relist-count, CVSG, Term 2025, and paid-petition cuts.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '594 U.S. 413' --limit 8 --corpus-backend ranged`
  - Failed before any results because the runner could not resolve the ranged corpus endpoint. No `ranged corpus reads: ...` line was printed.

## CourtListener MCP

- Opinion search for `"uninjured class members" certification TransUnion` across the Supreme Court and federal courts of appeals; returned one D.C. Circuit result that did not materially inform the forecast.
- Supreme Court opinion search by case name for *Laboratory Corporation of America Holdings v. Davis* in 2025; returned no result.
- Supreme Court opinion search for `LabCorp Davis 24-304 class certification` in 2025; returned *Laboratory Corp. of America Holdings v. Davis*, 605 U.S. 327 (2025).
- Repeated the *LabCorp* search requesting cluster and opinion identifiers; identified combined-opinion record 11065594.
- Retrieved CourtListener opinion record 11065594. It confirmed the June 5, 2025 DIG and Justice Kavanaugh's dissent stating that he would decide the Rule 23 question and bar a damages class containing injured and uninjured members.

No web searches were used.
