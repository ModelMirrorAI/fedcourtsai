# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-18.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, `event.yaml`, `metrics/statpack.md` (modern cert by disposition, by originating circuit, relist/CVSG/salience cuts, per-Term table and the sal-v4 segment band table), `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`.

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73358839 --event evt-petition-disposition --role predictor` — path resolution only.
- `uv run fedcourts open-events --court scotus --docket 73281689` — confirms the companion 25-1201 is unresolved in the corpus (`evt-petition-disposition` open). No transfer line (open-events prints none).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` — stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. Returned recent granted rows (mostly substantive applications and OT2025 grants); used only as a sanity check on what recent grants look like, not as an anchor.

## CourtListener MCP

1. `search` type=d court=scotus docket_number=25-1201 — 0 results.
2. `search` type=d court=ca5 docket_number=24-40792 — found *Texas Top Cop Shop v. Blanche*, docket 69450356, filed 2024-12-09, not terminated (the Fifth Circuit appeal remains pending).
3. `search` type=d court=scotus q="National Small Business United" — 0 results.
4. `call_endpoint` dockets court=scotus docket_number=25-1201 — found docket 73281689, *National Small Business United v. Bessent*, filed 2026-04-21, not terminated.
5. `call_endpoint` docket-entries docket=73281689 — 0 entries (CourtListener carries no entries for this SCOTUS docket).

## Web

1. WebSearch: `"National Small Business United" v. Bessent 25-1201 Supreme Court brief in opposition Solicitor General Corporate Transparency Act 2026` — surfaced the OSG brief page and Thomson Reuters coverage.
2. WebSearch: `FinCEN Corporate Transparency Act final rule 2026 beneficial ownership reporting domestic companies exempt status` — surfaced the FinCEN/Treasury releases and the Federal Register notice (final rule published Aug 14, 2026; issued Aug 11).
3. WebFetch https://www.justice.gov/osg/brief/national-small-bus-united-v-bessent — metadata only: petition-stage brief in opposition in 25-1201 (page lists a September 1, 2026 date; the docket shows the filing on Aug 21, 2026). Brief text not read.
4. WebFetch https://tax.thomsonreuters.com/news/corporate-transparency-act-challenges-still-pending-as-scotus-term-wraps-up/ — July 7, 2026 article: government waived response in 25-1290; response in 25-1201 extended; 25 states as amici.
5. WebFetch https://tax.thomsonreuters.com/news/group-says-government-is-ignoring-constitutional-elephant-in-corporate-transparency-act-dispute/ — SG's opposition (Aug 21, 2026) argues the Aug 14 final rule removes practical significance / moots the case; NSBU reply (Sept 9) argues voluntary cessation; distributed for Sept 28 conference.
6. WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/25-1201.html — companion docket entries: three response extensions (to June 22, July 22, Aug 21), opposition filed Aug 21, distributed Sept 9 for the Sept 28 conference, reply filed Sept 9.

None of the above surfaced a disposition of this petition or of the companion; both remain pending for the September 28, 2026 conference. Nothing under `data/qp-topics/` was read.
