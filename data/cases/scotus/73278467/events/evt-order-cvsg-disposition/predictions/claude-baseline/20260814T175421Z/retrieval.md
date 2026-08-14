# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-14, event.yaml, context.json,
petition.txt, brief-in-opposition.txt, questions-presented.txt,
documents.json) and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --disposition granted --era 2020s
  --corpus-backend service`
  - `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
  - Low value for this cell: most returned rows were application dockets
    (`25Annn` time-extension requests) whose `granted` disposition is the
    extension grant, not a cert grant — noted in `flags.json` and
    `tooling.json`.

## CourtListener MCP

- `search` (type=o, court=scotus, q="Hecox transgender", filed_after
  2026-01-01) → found *West Virginia v. B.P.J.*, No. 24-43, decided
  2026-06-30 (cluster 10882186).
- `get_endpoint_item` (clusters/10882186) → Kavanaugh authorship confirmed;
  no syllabus text ingested.
- `search_document` / `read_document` (opinion 11349709) → no text available
  on CourtListener yet for the opinion.

## Web

- Search: "West Virginia v. B.P.J. Little v. Hecox Supreme Court decision
  holding transgender athletes heightened scrutiny" → SCOTUSblog/CBS
  coverage: Court upheld both state laws, Kavanaugh majority, 2026-06-30.
- Search: "B.P.J. Kavanaugh opinion level of scrutiny transgender
  classification intermediate scrutiny equal protection 'biological sex'
  holding" → coverage (SCOTUSblog, Law Dork, The Federalist) confirming the
  opinion applied intermediate scrutiny on a biological-sex framing and
  expressly did **not** resolve whether heightened scrutiny applies to
  transgender classifications.

Both web searches concern companion/related litigation decided before this
cell's snapshot — legitimate forward signal for a forward-mode cell. No
search touched this petition's own disposition, which does not yet exist.
