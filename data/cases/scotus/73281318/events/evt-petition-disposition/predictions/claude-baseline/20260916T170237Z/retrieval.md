# Retrieval log

Provisioned inputs read: `record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, `record/documents/brief-in-opposition.txt`, the event definition, and the committed `metrics/statpack.md` (modern discretionary-cert disposition, relist-count, CVSG, salience-band, per-Term, and sal-v4 segment tables).

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
  Returned recent granted SCOTUS rows dominated by substantive emergency applications; not comparable priors for a state-court cert petition and not used in the number.

## CourtListener MCP lookups

- `search` (type opinion, court scotus, filed after 2026-01-01, q "Case v. Montana" emergency aid): one hit, Case v. Montana, No. 24-624, cluster 10774335, decided 2026-01-14.
- `read_document` (opinion 11240920, chunk 0 of 7): syllabus and opening of the opinion of the Court. Used to confirm the holding (Brigham City's objective-reasonableness standard applies without a probable-cause gloss; entry upheld; unanimous, with Sotomayor and Gorsuch concurrences) and the decision date relative to the state-court rulings in this case.

No lookup touched this case's own docket, disposition, or post-snapshot history. No web searches.
