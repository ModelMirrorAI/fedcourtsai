# Retrieval log

## Corpus tooling

1. `uv run fedcourts paths --court scotus --docket 73299074 --event evt-petition-disposition --role predictor`
2. `uv run fedcourts query --court scotus --include-applications --era 2020s --limit 300`
   - stderr: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Purpose: find mandamus / "In re" priors. Result: 300 rows ranked by recency, 233 of them granted time-extension applications; one "In re" row (In re J. E. Pendleton, 26A133, denied). No usable mandamus-petition population.
3. `uv run fedcourts query --court scotus --include-applications --disposition granted --limit 300`
   - stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   - Purpose: check whether any granted row is an "In re" / mandamus matter. Result: none among 300 granted rows.
4. `metrics/statpack.md` (committed): modern discretionary-cert base rate, relist-count and CVSG cuts (paid scored segment), per-Term table, and the sal-v4 segment base rate by salience band table.

## CourtListener MCP

1. `search` type=d, court=scotus, docket_number=25-1252 → 0 results.
2. `search` type=r, q=Devillier, court=[ca5, txsd] → located S.D. Tex. 3:20-cv-00223 (docket 17305392) and Fifth Circuit 21-40750 (docket 65740038).
3. `get_endpoint_item` dockets/73299074 → case name, docket number 25-1252, filed 2026-05-05, not terminated, last modified 2026-06-24.
4. `search` type=r, q=Devillier, court=ca5 → Fifth Circuit dockets 21-40750 (terminated 2024-09-26) and 21-90043; no later Devillier docket.
5. `call_endpoint` docket-entries, docket=17305392, date_filed >= 2024-04-01 → 42 entries: remand history, motion to remand (Dkt. 174), M&R (Dkt. 186, 2026-01-05), objections, order adopting (Dkt. 188, 2026-04-09).
6. `call_endpoint` recap-documents, docket_entry=449207314 → recap document 463995305 (Memorandum and Recommendations, 12 pages).
7. `read_document` recap_document_id=463995305 → full text of the magistrate judge's memorandum and recommendation.
8. `search` type=d, q=Devillier, court=[ca5, scotus], filed_after=2025-06-01 → 0 results.
9. `search` type=r, case_name=Devillier, court=ca5, filed_after=2025-01-01 → 0 results.

## Web fetches

1. `https://www.supremecourt.gov/DocketPDF/25/25-1252/407818/20260501162835028_25-%20Petition.pdf` → failed, content over the fetch tool's 10 MB limit; petition text not read.
2. `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/25-1252.html` → live docket page; two entries (petition filed Apr 24, 2026; distributed Jun 24, 2026 for the Sept 28, 2026 conference), matching the provisioned snapshot.

Nothing retrieved concerned this petition's disposition; the case is pending as of the retrieval.
