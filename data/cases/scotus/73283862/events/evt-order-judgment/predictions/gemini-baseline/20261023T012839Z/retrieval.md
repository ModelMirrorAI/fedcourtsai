# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 24-7420 --limit 5`
   - Transfer: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Purpose: Checked docket number `24-7420` (initial typo for *Fernandez v. United States*, No. 24-7240).
2. `uv run fedcourts query --court scotus --docket-number 24-7240 --limit 5`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Purpose: Retrieved corpus prior `scotus/72486702` (*Luis Fernandez v. United States*, No. 24-7240), confirming certiorari was denied on `2025-10-14` on the underlying Question 1 *Beeman*/*Fernandez* issue.
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --include-open --limit 10`
   - Transfer: `ranged corpus reads: 31 GET(s), 8126464 byte(s)`
   - Purpose: Checked recent OT2026 granted cases in the corpus for cohort context.

## CourtListener MCP and Web Lookups

- None (all case filings, lower-court orders, and precedent discussions were provisioned in `record/documents/` and `record/snapshots/2026-10-13.json`).
