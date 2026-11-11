# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Stderr transfer line: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Returned 5 recent 2020s SCOTUS granted rows (including recent OT2026 cert grants `25-1408`, `26-12`, and `26-204`, showing typical pre-grant distribution counts of 2–4).

## CourtListener MCP Lookups

None (the Tenth Circuit's published opinion and lower-court docket summary were fully provisioned in `record/documents/decision-below.txt`, `record/documents/lower-court-docket.txt`, and Appendix A of `record/documents/petition.txt`).

## Web Searches

None.
