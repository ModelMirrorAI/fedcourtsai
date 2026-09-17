# Retrieval log

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73361381 --event evt-petition-disposition --role predictor`
  (no transfer line; path resolution only)
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
  Returned four substantive emergency applications (People Not Politicians
  v. Onder; NRCC v. Brown; National Park Service v. National Trust; Trump v.
  California) and one paid cert grant (Jouppi v. Alaska, scotus/73275187).
  None comparable to a pro se state-court contract-limitations petition.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 3`
  stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
  Returned three recently denied applications (26A-series), not cert petitions.
- Base rates: read the committed `metrics/statpack.md`, sections "Modern
  discretionary-cert petitions by disposition", "Cert petitions by relist
  count", "by CVSG status", "by salience band", "SCOTUS cert petitions by
  Term", and "Segment base rate by salience band (sal-v4)".

## CourtListener MCP server

1. `search` type=o, q=`Chaganti "Cincinnati Insurance"`, court=[ohioctapp, ohio], filed_after=2024-01-01: 0 results (court filter mismatch).
2. `search` type=d, court=scotus, docket_number=25-1291: 0 results (the docket index did not match).
3. `search` type=d, court=scotus, party_name=Chaganti: 0 results.
4. `search` type=o, q=`Chaganti Cincinnati Insurance 2305.06`: 1 result, Chaganti v. Cincinnati Ins. Co., 2025-Ohio-1982, cluster 10597526, opinion 11064114.
5. `search` type=o, neutral_cite=2025-Ohio-1982: same single result.
6. `call_endpoint` dockets, court=scotus, docket_number=25-1291: docket id 73361381, filed 2026-05-19, `date_terminated` null.
7. `search` type=o, q=`"Naren Chaganti"`, newest first: 42 results, including Chaganti v. Comm'r, No. 18-1425 (SCOTUS, June 17, 2019, cert denied) and In re Chaganti (D.C. Ct. App. 2016).
8. `read_document` opinion_id=11064114, chunks 0 to 4 (full text, 37,346 chars): the Ohio Tenth District opinion, decided June 3, 2025.
9. `call_endpoint` docket-entries, docket=73361381: 0 results (CourtListener holds no entries for this SCOTUS docket).

Ten MCP calls in total across nine lookups (one search response contained two identical hits). No web searches. Nothing retrieved postdates the snapshot or reveals this case's disposition.
