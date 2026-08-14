# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-14, `event.yaml`,
`record/context.json`, `record/documents/` petition text + questions
presented, and the committed `metrics/statpack.md`):

## Corpus (`fedcourts query`)

- `uv run fedcourts query --court scotus --citation "143 F.4th 411"`
  — stderr: `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`, plus the
  coverage-gap note (only 161 of 590,020 scotus rows carry citation data; the
  filter is an own-cites lookup). No rows returned — the documented sparse
  -filter gap, not evidence of no precedent.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. Returned 7 rows,
  mostly `25Axxxx` application-extension dockets carrying `disposition:
  granted` (extension grants, not cert grants) plus one true cert grant
  (Jouppi v. Alaska, 25-246). Not usable as priors for this cell; nothing from
  it informed the numbers.

## CourtListener MCP

- `search` (opinions, cadc, `"In re United States" mandamus military
  commission plea`, filed 2025-07-01..2025-07-20) — confirmed the decision
  below: In re: United States of America, No. 25-1009, filed 2025-07-11 (two
  opinion records, consistent with a majority plus dissent). Judge fields were
  empty.
- `get_endpoint_item` (opinions 10631648 → cluster 10165052; opinions
  10633308 → cluster 10166712; clusters 10165052) — the cluster lookups
  resolved to an unrelated case (Turner-Pugh v. Monroe County Board of
  Education), an apparent index/ID mismatch; panel composition was not
  recovered from CourtListener and is taken from the petition's own account of
  a divided panel.
- `search` (dockets, scotus, docket_number `25-1335`; then q=`Atash`) — 0
  results both times: CourtListener does not index SCOTUS dockets, so the
  companion petition bin 'Atash v. United States, No. 25-1335 (named in the
  petition's related proceedings) could not be checked.

No web searches. Nothing retrieved concerned this petition's own disposition,
which does not yet exist (forward mode).
