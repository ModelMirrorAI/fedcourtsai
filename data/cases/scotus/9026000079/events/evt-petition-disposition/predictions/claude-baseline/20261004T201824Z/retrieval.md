# Retrieval log

## Corpus (`fedcourts`)

- `uv run fedcourts query --court scotus --era 2020s --limit 12`
  stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
  (recency-ranked recent SCOTUS rows, mostly October 2026 applications; not used in the anchor)
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 40`
  stderr: `ranged corpus reads: 50 GET(s), 13107200 byte(s)`
  (40 granted rows, 4 from ca9, all with distribution_count 2-4; used only as a shape check against the statpack relist cut)
- `metrics/statpack.md`: modern discretionary-cert by disposition, by originating circuit, relist-count cut, CVSG cut, salience-band cut, per-Term table, and the sal-v4 segment base-rate table (anchor: pooled `baseline` bracketed `reached`, Terms 2017-2025).

## CourtListener MCP

- `search` type=o, q="Acosta-Tapia", court=ca9, filed_after 2025-06-01: 0 results
- `search` type=o, docket_number=25-2460, court=ca9: 0 results
- `search` type=o, q="Acosta Tapia" OR "Acosta-Tapia" OR "Tapia v. Bondi", filed_after 2025-09-01: 0 results
- `search` type=d, docket_number=25-2460, court=ca9: 1 result, Acosta-Tapia v. Bondi, docket id 72369758
- `search` type=d, docket_number=26-79, court=scotus: 0 results
- `search` type=d, case_name="Acosta Tapia", court=[ca9, scotus]: 0 results
- `call_endpoint` docket-entries, docket=72369758: 39 entries (petition for review filed 2025-04-16; stay of removal; amicus motion by NILA denied; submitted without argument 2026-01-08; memorandum disposition 2026-01-15 "PETITION DISMISSED"; panel rehearing denied 2026-02-26)
- `call_endpoint` clusters, docket=72369758: 0 results (memorandum not indexed as an opinion)
- `get_endpoint_item` dockets/72369758: field error (invalid field name requested); not retried
- `read_document` recap_document 470957078 (memorandum): no text available
- `read_document` recap_document 470957055 (NILA amicus brief): no text available
- `search` type=o, q="Acosta-Tapia Bondi": 0 results
- `search` type=o, case_name="Acosta-Tapia v. Bondi": 0 results

## Web

- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/26-79.html — live docket as of 2026-10-04: entries match the snapshot; no grant, denial, relist, redistribution, or response request; no petition PDF linked.
- WebFetch https://cdn.ca9.uscourts.gov/datastore/memoranda/2026/01/15/25-2460.pdf — Ninth Circuit memorandum (binary saved; text extracted locally with pdftotext). This is the source of the case facts in `reasoning.md`.
- WebSearch "Acosta-Tapia" Ninth Circuit 25-2460 OR "26-79" Supreme Court certiorari — surfaced the memorandum URL above; no coverage of the cert petition.
- WebSearch "Riley v. Bondi" reinstatement withholding-only petition for review 30-day deadline equitable tolling certiorari petition 2026 — background on Riley v. Bondi, 606 U.S. 259 (2025); no pending Supreme Court vehicle on post-Riley tolling surfaced.

None of the retrieval surfaced this petition's disposition; the case is pending.
