# Evaluator Retrieval Log (`gemini-judge`, run `20261117T154407Z`)

## `fedcourts` CLI Lookups

1. `uv run fedcourts paths --court scotus --docket 9026000420 --event evt-petition-disposition --role evaluator`
   - Resolved case, corpus, event, and outcome paths (no ranged corpus reads).
2. `uv run fedcourts statpack-at data/cases/scotus/9026000420/record/blinded/<alias>/ --ref origin/main --out-dir ...` (run for `claude-baseline`, `codex-baseline`, `gemini-baseline`, and into the session scratch directory to read `statpack.md`)
   - Resolved all three candidates' placement statpack to build `dedb32b153e67d254af10083c3ee247cecd56116` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, landed `2026-10-31T10:28:26-04:00`), matching `sal-v6` figures cited by the candidates (no ranged corpus reads).
3. `uv run fedcourts query --court scotus --docket-number 26-1`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Verified *Sunoco, Inc. (R&M), et al. v. Perry Cline* (`scotus/9026000001`), cert denied `2026-10-05`.
4. `uv run fedcourts query --court scotus --docket-number 25-677`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified *City of Cleveland, Ohio v. Albert Pickett, Jr.* (`scotus/73279523`), open with `distribution_count: 4` (last distributed `2026-05-28`).
5. `uv run fedcourts query --court scotus --docket-number 25-625`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified *Takeda Pharmaceutical Company Limited v. Painters and Allied Trades District Council 82 Health Care Fund* (`scotus/73279069`), cert denied `2026-03-23`.
6. `uv run fedcourts query --court scotus --docket-number 24-304`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified *Laboratory Corporation of America Holdings v. Luke Davis* (`scotus/69981163`), cert granted `2025-01-24`, `dismissed-as-improvidently-granted` `2025-06-05`.

## CourtListener MCP Lookups

- None.

## Web Searches

- None.
