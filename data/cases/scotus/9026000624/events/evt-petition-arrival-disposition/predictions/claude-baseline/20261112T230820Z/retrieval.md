# Retrieval log

Beyond the provisioned inputs:

- `metrics/statpack.md` — read the "Segment base rate by salience band" table (baseline column) and the originating-circuit cut (ca4 row).
- `uv run fedcourts query --help` — usage text.
- `uv run fedcourts query --court scotus --docket-number 25-640` — returned this case's prior docket (GVR, cert granted 2026-03-23, two distributions). This and the next command ran in one shell call and printed one transfer line between them: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`.
- `uv run fedcourts query --court scotus --disposition gvr --era 2020s` — returned recent GVR rows (several federal-respondent and Monsanto petitions); none bore on this question, and I did not use them.

No CourtListener MCP calls and no web searches.
