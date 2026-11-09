# Retrieval record

## Baseline and repository reference material

Read the prediction prompt; prediction, flags, and tooling schemas; the event definition; the November 9, 2026 provisioned snapshot; document manifest; questions presented; the petition's question, introduction, factual and procedural account, cert arguments, conclusion, and relevant appended opinion/order passages; Appendix H's contents; context; same-question results; and the official Vide companion snapshots and relation manifest. Read `metrics/statpack.md`, particularly the paid-segment relist, CVSG, amicus, salience, and sal-v8 per-Term tables. Only strictly prior Terms and the frozen context anchor informed calibration.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000292 --event evt-petition-disposition --role predictor` failed before execution because the default uv cache was read-only. No corpus data returned.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000292 --event evt-petition-disposition --role predictor` succeeded and confirmed the case and event paths. No outcome path was opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. A second identical help invocation, with output restricted to its middle section, checked available filter flags.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '578 U.S. 212' --decided-before 2026 --limit 3` returned no matching rows and explicitly warned that the reporter-citation column is sparsely populated. This was a Bank Markazi precedent lookup, not a query for the current petition.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` returned Goldman Sachs Bank USA v. Brown, No. 25-1408; U.S. DOGE Service v. U.S. District Court, No. 25-1103; and Berry v. United States, No. 25-7026. They show heterogeneous grant trajectories, not a subject-specific estimator, and did not determine the forecast. The year filter uses derived Term/year, so returned resolution dates can fall in calendar 2026; this is a forward cell and none concerns the target petition.

   `ranged corpus reads: 33 GET(s), 8650752 byte(s)`

## Web searches attempted

Both `web.run` search batches returned no visible results; no web result or disposition claim informed the prediction.

1. Queries: `site.ca11.uscourts.gov Stansell 45 F.4th 1340 2022 agency instrumentality`; `site.ca2.uscourts.gov Havlish August 26 2025 23-258 Taliban`. The latter was explicitly for the pre-petition appellate judgment, not the Supreme Court's outcome.
2. Queries: `"Stansell" "45 F.4th" "2022"`; `site.media.ca11.uscourts.gov "Stansell" "2022" "ever"`.

## CourtListener MCP calls

1. `search(type=o, court=ca11, citation="45 F.4th 1340", num_results=3)`: no matches.
2. `search(type=o, court=ca11, q='Stansell "1350"', filed_before=2023-01-01, num_results=3)`: returned Stansell v. Lopez Bello, 40 F.4th 1308, and two unrelated opinions. None was treated as the requested temporal-rule authority.
3. `search(type=o, court=ca11, case_name=Stansell, filed_after=2022-08-01, filed_before=2022-09-30, num_results=5, fields=[caseName,dateFiled,citation,opinions,absolute_url])`: found Keith Stansell v. UBS Financial Services, Inc., August 23, 2022, No. 20-11736, opinion **7802935**. The reporter citation was absent from its metadata; identity was checked by date, case, docket, and text.
4. `search_document(opinion_id=7802935, query=Kirschenbaum, snippet_size=2000)`: located its discussion of the temporal rule and past affiliation.
5. `read_document(opinion_id=7802935, chunk_index=3, chunk_size=8000)`: read the pertinent printed pp. 15–18 discussion, including its qualification of the apparent disagreement with Kirschenbaum.
6. `search(type=o, court=ca2, docket_number=23-258, filed_after=2025-08-25, filed_before=2025-08-28, num_results=2, fields=[caseName,dateFiled,citation,opinions,absolute_url])`: matched Havlish v. Taliban; Aliganga v. Taliban, August 26, 2025, opinion **11127439**, to the lower-court judgment in the provisioned petition.
7. `search_document(opinion_id=11127439, query="date that", snippet_size=1300)`: verified the blocking-date holding and located the majority's rationale and Sullivan's response.
8. `read_document(opinion_id=11127439, chunk_index=[12,13], chunk_size=8000)`: retrieved the majority's timing analysis and disposition, roughly printed pp. 48–55, filling material omitted from the provisioned appended opinion. This was the lower-court decision under review, not subsequent Supreme Court history.
9. `search(type=o, court=ca9, citation="825 F.3d 949", num_results=1, fields=[caseName,dateFiled,citation,opinions,absolute_url])`: found Bennett v. Islamic Republic of Iran, lead opinion **8414040** and separate opinion 8414041. Only the lead opinion's TRIA discussion was used.
10. `search_document(opinion_id=8414040, query=when, snippet_size=450)`: located contextual passages but no clear holding of a later-acquired instrumentality timing rule.
11. `search_document(opinion_id=8414040, query=963, snippet_size=1400)`: searched the ownership section's reporter-page context; HTML citation matches made this imprecise.
12. `search_document(opinion_id=8414040, query="the blocked assets must", snippet_size=1000)`: isolated the TRIA ownership discussion at printed pp. 963–64. It supports a property-ownership requirement, not an express resolution of this petition's temporal question.

No current Supreme Court outcome, another predictor's output, evaluation, or topic-label artifact was retrieved. No opinion bodies were downloaded through a direct CourtListener REST fallback. The final cell-validation command is a local output check, not an evidentiary lookup.
