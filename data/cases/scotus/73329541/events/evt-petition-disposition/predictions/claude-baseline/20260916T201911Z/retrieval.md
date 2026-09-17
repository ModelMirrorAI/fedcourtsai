# Retrieval log

## Provisioned inputs read
- `record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, `events/evt-petition-disposition/event.yaml`.
- `metrics/statpack.md` sections: modern discretionary-cert by disposition, by originating circuit, relist count, CVSG status, salience band, SCOTUS cert petitions by Term, Segment base rate by salience band (sal-v4).

## Corpus lookups
1. `uv run fedcourts query --court scotus --era 2020s --disposition granted` (default limit 20) — returned recency-ranked recent grants and substantive stay applications; no topical overlap with this petition, not used in the number.
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`

## CourtListener MCP lookups (17 calls)
1. `search` type=d court=scotus docket_number=25-1274 — 0 results (CourtListener carries no SCOTUS docket for this case).
2. `search` type=o court=scotus case_name="Bowe v. United States" filed_after=2025-10-01 — 1 result, cluster 10772450, decided 2026-01-09, No. 24-5438.
3. `search` type=o court=scotus q="2241" AND "2244(d)" AND "limitations" filed_after=2015-01-01 — 5 results, all Edwards v. Vannoy (2021), not on point.
4. `call_endpoint` opinions cluster=10772450 — opinion id 11239035 (combined, 61 pages).
5. `search` type=o court=ca10 case_name="St. Clair" filed_after=2025-06-01 — 0 results.
6. `search` type=o court=oked case_name="St. Clair" filed_after=2024-01-01 — 0 results.
7. `search` type=o court=ca7 q="Cox v. McBride" AND "2241" AND "2244(d)" filed_after=2015-01-01 — 0 results.
8. `search_document` opinion 11239035 query="we hold" — 0 matches.
9. `search` type=o court=ca10 q="St. Clair" AND "2241" AND "Executive Agreement" filed_after=2025-01-01 — 0 results.
10. `search` type=r court=ca10 docket_number=24-7090 — 1 result: St. Clair v. Quick, docket 71675302; entry 21 (2025-10-17) "Case termination for COA", document not available.
11. `search` type=r court=oked q="St. Clair" AND "2241" filed_after=2024-01-01 — 1 result: St. Clair v. Quick, 6:24-cv-00275, docket 69989590; doc 19 (2026-03-24) Opinion and Order dismissing petition as untimely, COA denied.
12. `search` type=o court=ca7 q="Cox v. McBride" filed_after=2016-01-01 — 0 results.
13. `read_document` recap_document_id=473438325 — full text of the E.D. Okla. March 24, 2026 opinion (10 pages). Confirms: first § 2241 petition (No. 23-CV-338) dismissed as time-barred Sept. 16, 2024; Tenth Circuit denied COA Oct. 17, 2025 (No. 24-7090); second petition untimely under § 2244(d)(1)(A) and (D), no statutory or equitable tolling.
14. `search_document` opinion 11239035 query="Held:" — 1 match; syllabus holding 1 (§ 2244(b)(3)(E) does not bar certiorari review of federal prisoners' successive § 2255 authorization denials).
15. `search` type=o q="Cox v. McBride" AND "2244(d)" AND "2241" filed_after=2020-01-01 (all courts) — 0 results.
16. `read_document` opinion 11239035 chunk 2 of 40 (4000 chars) — syllabus holding 2 (§ 2244(b)(1) does not apply to federal prisoners' successive § 2255 motions) and the reasoning that § 2244's strict requirements target state prisoners.

No web searches. Nothing retrieved touches this petition's disposition; the conference is set for 2026-09-28, after this run.
