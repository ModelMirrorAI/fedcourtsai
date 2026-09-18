# Retrieval record

The provisioned event, context, September 18 snapshot, document manifest, questions presented, petition, and opposition were the baseline. No Supreme Court disposition or subsequent-history search was made.

## Committed aggregate context

- Read `metrics/statpack.md`: modern discretionary cert, paid-segment relist/CVSG cuts, and sal-v4 per-Term reached-band rates.
- Read the structure and relevant fields of `metrics/statpack.json`. Pooled only the rendered 2017–2024 elevated reached rates for this Term-2025 cell: 484 / 2,810 = 0.1722419929.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json`, returning `55121cdb8 2026-09-14T11:02:00Z`. This dates the committed pack, not the remote corpus.
- No `fedcourts query`, `open-events`, corpus pull, or live aggregate lookup was used. Consequently there was no ranged-corpus transfer line.

## Web attempts: no usable returned content

1. Opened the appendix PDF URL explicitly linked in the provisioned March 19 petition entry: Supreme Court DocketPDF path `25/25-1108/401277/20260319101935248_260309a%20Appendix%20for%20efiling.pdf`. The tool returned no content.
2. Repeated that same direct appendix open; again no content.
3. Submitted a combined search for `site.ca11.uscourts.gov "Johnson" "1292" "2024" video complaint` and `site.supremecourt.gov "Rule 10" "compelling reasons"`. No results were surfaced. No web content was used.

## CourtListener MCP: six calls

1. `search(type="o", citation="107 F.4th 1292", num_results=2, fields=["caseName", "dateFiled", "opinions", "absolute_url", "citation"])`: returned Charles Johnson, Jr. v. City of Atlanta, July 12, 2024, opinion 10467583, cluster 10000982.
2. `search_document(opinion_id=10467583, query="central", snippet_size=1700)`: inspected the opinion's centrality/authenticity requirements and treatment of video not referenced in the complaint. Relevant printed pages include 2 and 13–16. This is an unrelated prior, not this petition's outcome.
3. `search(type="o", citation="157 F.4th 1288", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url", "citation"])`: no result. This citation came from the provisioned petition's identification of the decision below.
4. `search(type="o", court="ca10", docket_number="24-2152", filed_after="2025-11-03", filed_before="2025-11-05", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url", "citation"])`: retrieved only the November 4, 2025 Tenth Circuit decision under review, Fuqua v. Santa Fe County Sheriff's Office, opinion 11196917, cluster 10730332. The narrow date and court filters targeted the pre-petition decision, not later history.
5. `search_document(opinion_id=11196917, query="even if", snippet_size=1900)`: inspected the alternative video analysis and related passages.
6. `read_document(opinion_id=11196917, chunk_index=4, chunk_size=8000)`: read the primary-source alternative analysis at printed pages 15–16 and the beginning of the immunity discussion, confirming that the court below addressed the Sixth Circuit standard even assuming it applied.

## Administrative checks

Read the prediction, tooling, and flags schema contracts and the repository path/serialization helpers. Ran the predictor-safe path resolver with the literal cell IDs. The first `uv` invocation failed because its default cache directory was read-only; subsequent invocations used `/tmp/uv-cache`. These were administrative operations, not substantive corpus retrieval.

No outcome-revealing material was returned, and no known outcome informed the forecast.
