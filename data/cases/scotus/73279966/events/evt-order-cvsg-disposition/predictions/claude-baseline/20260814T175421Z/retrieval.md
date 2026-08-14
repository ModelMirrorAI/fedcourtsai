# Retrieval log

Beyond the provisioned inputs (snapshot 2026-08-14, `record/context.json`,
`questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`,
`documents.json`, the committed `metrics/statpack.md`):

## Corpus

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  — stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`. Returned mostly
  extension applications labeled granted plus one recent cert grant; not
  informative for this cell, no follow-up queries run.

## CourtListener MCP

- `search(type=d, court=scotus, q="GEO Group Menocal")` — 0 results.
- `search(type=o, court=scotus, q="GEO Group Menocal")` — found
  *Geo Group, Inc. v. Menocal*, decided 2026-02-25 (published).
- `read_document(opinion_id=10800194, chunk 0)` — the linked text was an
  unrelated Pennsylvania Superior Court case (a CourtListener data mislink);
  discarded.
- `search(type=o, court=scotus, q="Menocal derivative sovereign immunity
  collateral order")` — confirmed the 2026-02-25 decision, opinion by Kagan.

No web searches. All retrieval was about related litigation and priors; no
lookup sought this petition's own disposition (forward cell — none exists).
