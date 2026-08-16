# Retrieval log

Beyond the provisioned inputs (snapshot, event, context, QP text, petition
text, brief-in-opposition text, `metrics/statpack.md`):

## Corpus tooling

- `uv run fedcourts query --court scotus --disposition granted --limit 5`
  → `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
  (recent granted-petition priors for context; none case-dispositive)

## CourtListener MCP

All calls were to verify the intervening decision the respondent's merits
brief relies on (FCC v. AT&T, decided 2026-06-04 — postdates model training,
predates this cell's snapshot; legitimate forward signal):

- `search` (opinions, scotus, q="FCC v. AT&T penalties adjudicate section 504
  trial de novo", filed_after 2025-10-01) → cluster 10870061
- `read_document` (opinion_id 10870061) → 404 (cluster id, not opinion id)
- `search` (opinions, scotus, q="FCC v. AT&T", filed 2026-06-01..2026-06-10,
  fields incl. `opinions`) → opinion id 11337518
- `read_document` (opinion 11337518, chunks 0–2 of 9) → syllabus, holding
  (§503(b)(4) forfeiture orders constitutional because §504 guarantees a
  subsequent trial de novo), lineup (Roberts for eight; Thomas dissenting)

## Web searches

None.
