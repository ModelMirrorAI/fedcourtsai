# Retrieval log

## Provisioned inputs (not retrieval)

Snapshot `record/snapshots/2026-07-01.json`; `record/context.json`;
`record/documents/questions-presented.txt`, `petition.txt`,
`brief-in-opposition.txt` (all fetched with text per `documents.json`);
`metrics/statpack.md` (committed base rates); `event.yaml`.

## Corpus tooling

No `fedcourts query` / `open-events` calls — the committed statpack's CVSG
cut, relist cut, and sal-v3 band table covered the priors this cell needed,
and none of `query`'s filters (court/disposition/era/judge/citation/topic)
selects the CVSG'd-petition population. No `ranged corpus reads` lines to
record.

## CourtListener MCP lookups (forward mode — unrestricted)

All aimed at the companion merits litigation this petition was held for;
none sought this petition's own disposition (none exists).

1. `search` (type=o, court=scotus, q=`Hecox OR "B.P.J."`, filed_after
   2025-07-01) → West Virginia v. B. P. J., No. 24-43, decided **2026-06-30**
   (cluster 10882186) — the same day as this docket's CVSG.
2. `read_document` (opinion_id=10882186, chunk 0) → HTTP 404 (the search hit's
   id is a cluster id, not an opinion id).
3. `get_endpoint_item` (clusters/10882186) → sub-opinion 11349709; judges
   "Brett Kavanaugh"; no syllabus.
4. `search_document` (opinion_id=11349709, "heightened scrutiny") → no text
   available for this document.
5. `read_document` (opinion_id=11349709, chunk 0) → no text available.

Net: B.P.J.'s decision date and existence were usable; its holding was not
retrievable from CourtListener at run time.

## Web searches

None.
