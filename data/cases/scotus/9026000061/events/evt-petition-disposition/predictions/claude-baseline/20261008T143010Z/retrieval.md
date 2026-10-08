# Retrieval log

Provisioned inputs read: `record/snapshots/2026-10-08.json`, `record/context.json`,
`record/documents/documents.json`, `record/documents/questions-presented.txt`,
`record/documents/petition.txt`, `events/evt-petition-disposition/event.yaml`,
`metrics/statpack.md`.

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  — stderr: `ranged corpus reads: 28 GET(s), 7274496 byte(s)`. Returned 8 rows
  (recent granted petitions and applications) with no caption or topic fields
  populated, so no subject-matched priors came from it.

## CourtListener MCP lookups

- `search` (type opinion, court ca9, q: Yonay Paramount "Top Gun" substantial
  similarity) — 1 result: *Yonay v. Paramount Pictures Corporation*, No. 24-2897,
  filed 2026-01-02, status Published, cluster 10768252.
- `get_endpoint_item` (clusters, 10768252) — sub-opinion 11234837, Published,
  no panel metadata populated.
- `read_document` (opinion 11234837, chunk 0 of 5, 12000 chars) — header,
  staff summary, counsel, and the opening of the opinion: panel Hurwitz, Miller,
  Sung; opinion by Judge Miller; summary judgment affirmed on substantial
  similarity, expert rulings, and the contract claim.

## Web fetches

- `https://www.courtlistener.com/opinion/10768252/yonay-v-paramount-pictures-corporation/`
  — page returned blank to the fetcher; superseded by the MCP `read_document` call.
- `https://www.supremecourt.gov/docket/docketfiles/html/public/26-61.html` —
  live docket; entries identical to the provisioned snapshot (last entry
  August 20, 2026; response due October 16, 2026). No disposition surfaced.
