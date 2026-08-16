# Retrieval log

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --disposition granted --limit 3`
   — service probe; returned recent granted cert rows (not used substantively).
   Stderr: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
2. `uv run fedcourts query --court scotus --include-applications --limit 8`
   — recent application-docket rows (mostly extensions; one substantive
   capital denial, 26A175).
   Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
3. `uv run fedcourts query --court scotus --include-applications --disposition denied --limit 40`
   — 24 resolved substantive denied applications, used as shape priors
   (pro se and court-as-respondent applications denied within days, no
   escalation signals).
   Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`

## CourtListener MCP

1. `search(type=d, court=ca9, docket_number=25-2374)` — 0 results.
2. `search(type=r, court=ca9, q='Watkins "25-2374"')` — 0 results.
3. `search(type=d, court=[ca9, azd], case_name=Watkins, filed_after=2024-06-01)`
   — 11 results; established the applicant as a serial pro se litigant in the
   District of Arizona (Santander, Becton Dickinson, SSA, state-agency suits).
   Did not query this application's own SCOTUS docket or disposition.

## Base rates

Committed `metrics/statpack.md`, "The interim docket (applications)" section —
strictly-prior pool computed at 47 resolved substantive (OT2024), below the
50-resolved floor, so no published baseline; section counts used as shape only.
