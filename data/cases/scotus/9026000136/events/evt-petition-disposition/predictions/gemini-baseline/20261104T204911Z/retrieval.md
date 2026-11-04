# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1230`
   - Transfer: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned 1 row (`scotus/73265705`, *Google LLC v. VirtaMove, Corp., et al.*, docket `25-1230`, `disposition: "denied"`, `date_cert_denied: "2026-10-19"`, `distribution_count: 2`).

2. `uv run fedcourts query --court scotus --docket-number 26-73`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/9026000073`, *Intel Corporation, et al. v. John A. Squires, Under Secretary of Commerce for Intellectual Property and Director, United States Patent and Trademark Office, et al.*, docket `26-73`, `disposition: null`, pending).

3. `uv run fedcourts query --court scotus --docket-number 26-198`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/9026000198`, *Kahoot! AS v. Interstellar Inc., et al.*, docket `26-198`, `disposition: null`, pending).

4. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Result: Returned 10 recent resolved SCOTUS rows from the 2020s era.

## CourtListener MCP Lookups

- None attempted.

## Web Searches

- None attempted.
