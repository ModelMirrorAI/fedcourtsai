# Retrieval log

## Provisioned inputs read
- `record/context.json`, `record/snapshots/2026-09-15.json`
- `record/documents/documents.json`, `questions-presented.txt`, `petition.txt` (QPs, statement, procedural history, reasons for granting, conclusion, and the Second Circuit opinion's opening pages in Appendix A)
- `events/evt-petition-arrival-disposition/event.yaml`
- `metrics/statpack.md` (modern-cert disposition, relist, CVSG, salience-band cuts; per-Term table; "Segment base rate by salience band (sal-v4)")

## Corpus lookups
1. `uv run fedcourts query --court scotus --disposition gvr --era 2020s`
   stderr: `ranged corpus reads: 45 GET(s), 11665408 byte(s)`
   20 rows, nearly all companion/hold petitions GVR'd in the June 29–30, 2026 clean-up order lists with 2–4 distributions each.

## CourtListener MCP lookups (forward mode; none surfaced this case's disposition)
1. `search` type=d, court=scotus, docket_number=26-304 (the *Jackson* lead petition) — 0 results.
2. `search` type=d, court=scotus, docket_number=26-348 (this docket) — 0 results.
3. `search` type=o, q="Vacancies Reform Act" "first assistant" "acting United States Attorney", filed_after 2025-06-01 — 4 results: OLC opinion (2026-09-04), CA2 *In re Grand Jury Subpoenas* (cluster 10954424, 2026-08-21), CA9 *United States v. Salazar Del Real* (cluster 10951924, 2026-08-17), CA3 *United States v. Giraud* (cluster 10745263, 2025-12-01).
4. `call_endpoint` clusters id=10951924 (fields: judges, syllabus, sub_opinions) — metadata only.
5. `call_endpoint` clusters id=10954424 — metadata only.
6. `call_endpoint` dockets court=scotus docket_number=26-304 — 0 results.
7. `search` type=o, court=ca9, q="United States v. Jackson" "Vacancies Reform Act", filed_after 2026-08-01 — 0 results.
8. `call_endpoint` opinions id=11419516 (author/type/download_url) — metadata only.
9. `read_document` opinion_id=11419516 chunk 0 of 14 (6000 chars): the CA9 opinion is *United States v. Jackson* (Nos. 25-6214 et al., consolidated with *Salazar Del Real* and *Enriquez*), panel Thomas, Miller, Blumenfeld (D.J.), opinion by Judge Miller, affirming disqualification of the putative Acting U.S. Attorney for Nevada; no dissent noted in the staff summary.

No web searches.
