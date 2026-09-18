# Retrieval log — claude-baseline, run 20260918T174135Z, scotus/73278467 evt-order-cvsg-disposition

Mode: `forward` (context.json). Retrieval unrestricted; nothing outcome-revealing was found — the petition remains pending with no Solicitor General brief as of the run date.

## Corpus tooling

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Returned 11 rows, ranked by recency: four 2026 emergency applications (26A326, 26A274, 26A203, 26A124) and seven cert grants (25-246, 25-238, 25-566, 25-965, 25-1311, 24-1016 with a 2025-10-06 CVSG, 24-6543). Not a useful comparison set for a CVSG'd prison equal-protection petition; used only to confirm the row shape.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned 7 rows, all September 2026 emergency-application denials. Not used.
3. `metrics/statpack.md` (committed): Modern discretionary-cert petitions by disposition; relist-count cut; CVSG cut; salience-band cut; SCOTUS cert petitions by Term; Segment base rate by salience band (sal-v4).

## CourtListener MCP

4. `search` type=d court=scotus docket_number=25-442 → 0 results.
5. `search` type=o court=scotus q=`Hecox OR "B.P.J."` filed_after 2026-01-01 → *West Virginia v. B. P. J.*, No. 24-43, cluster 10882186, filed 2026-06-30 (plus two unrelated *Landor* rows).
6. `get_endpoint_item` clusters/10882186 → judges "Brett Kavanaugh", date_filed 2026-06-30, empty syllabus.
7. `search` type=d court=scotus q=`Roybal Griffith` → 0 results.
8. `call_endpoint` dockets court=scotus docket_number=25-442 → docket id 73278467, date_filed 2025-10-10, date_terminated null.
9. `call_endpoint` opinions cluster=10882186 → one combined opinion, id 11349709, 77 pages.
10. `call_endpoint` docket-entries docket=73278467 → 0 entries (CourtListener carries none for this SCOTUS docket).
11. `read_document` opinion 11349709 chunks 0–1 → "No text is available for this document."
12–14. `search_document` opinion 11349709 for `quasi-suspect`, `Hecox`, `prison` → no text available.

## Web

15. WebSearch: `West Virginia v. B.P.J. Supreme Court decision June 30 2026 holding level of scrutiny transgender` → CRS LSB11454, supremecourt.gov 24-43 opinion PDF, NCLR commentary, Wikipedia, SCOTUSblog case page.
16. WebSearch: `Roybal v. Griffith 25-442 Supreme Court Solicitor General views transgender inmate Tenth Circuit` → SCOTUSblog case page and December 2025 relist-watch column, Washington Times petition coverage, supremecourt.gov docket and filings.
17. WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/25-442.html → nine proceedings entries, identical to the provisioned snapshot; last entry 6/30/2026 CVSG; no SG brief, no disposition.
18. WebFetch https://www.congress.gov/crs-product/LSB11454 → HTTP 403, not read.
19. WebFetch https://www.scotusblog.com/cases/roybal-v-griffith/ → same nine entries; one linked column (Dec 23, 2025 relist watch); no disposition shown.
20. WebFetch https://en.wikipedia.org/wiki/West_Virginia_v._B._P._J. → majority by Kavanaugh, J., joined by Roberts, Thomas, Alito, Gorsuch, Barrett; intermediate scrutiny applied, laws upheld; quasi-suspect-class question not addressed; Sotomayor, Kagan, Jackson dissenting; consolidated with *Little v. Hecox*.
21. WebFetch https://www.nclrights.org/what-the-supreme-court-did-not-decide-in-west-virginia-v-b-p-j/ → Court said the laws survive under either rational basis or heightened scrutiny and left the standard for transgender classifications formally unresolved; ruling confined to sports.

Nothing under `data/qp-topics/` was read. No prior prediction on this event was read.
