# Retrieval log — scotus/73281624, evt-petition-disposition, claude-baseline, 20260717T000329Z

Beyond the provisioned inputs (snapshot, questions-presented, petition, brief
in opposition) and the committed `metrics/statpack.md` base rates, I made the
following corpus lookups. All returned **zero priors** — the corpus's resolved
slice surfaced no similar antitrust / Parker-immunity cert petitions — so the
prediction rests on the provisioned documents plus statpack base rates.

1. `uv run fedcourts query --court scotus --topic "antitrust state action immunity Parker municipality" --limit 8 --corpus-backend ranged`
   - stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
   - 0 rows.
2. `uv run fedcourts query --court scotus --topic "antitrust" --limit 8 --corpus-backend ranged`
   - stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
   - 0 rows.
3. `uv run fedcourts query --court scotus --citation "Parker v. Brown" --limit 8 --corpus-backend ranged`
   - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
   - 0 rows.
4. `uv run fedcourts query --court scotus --topic "Sherman Act monopoly" --limit 8 --corpus-backend ranged`
   - stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
   - 0 rows.

No CourtListener MCP lookups and no web searches were made; the cell is
`forward` mode and the provisioned record was complete (petition, BIO, and QPs
all present with extracted text), so I did not need to retrieve this case's
docket or related litigation, and I made no query that could surface a
disposition for this still-pending petition.
