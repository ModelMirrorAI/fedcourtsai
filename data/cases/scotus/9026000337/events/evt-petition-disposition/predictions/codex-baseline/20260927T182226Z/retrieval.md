# Retrieval record

## Provisioned inputs

- Read event.yaml, record/context.json, and record/snapshots/2026-09-27.json for this cell.
- Read record/documents/documents.json and questions-presented.txt, and relevant petition.txt passages including the reasons for review, alternative certification request, and Appendix A's lower-court opinion. Did not independently verify every authority or every jurisdiction in the petition's survey.

## Committed reference material

- Read AGENTS.md, .github/prompts/predict.md, and the prediction, agent-tooling, and agent-flags schemas.
- Read metrics/statpack.md: modern discretionary-cert, paid relist and CVSG cuts, and sal-v4 prior-Term band table. Read metrics/statpack.json's corresponding Term segment records to pool baseline prefix_est_grant_rate weighted by prefix_weighted_resolved for 2017-2025: 638 / 12,720.
- Used git log restricted to metrics/statpack.md to identify its last committed update: September 26, 2026, 96ebdd342. No live corpus freshness inference follows from that date.
- Ran fedcourts paths --court scotus --docket 9026000337 --event evt-petition-disposition --role predictor. The first attempt failed on the default cache's read-only filesystem; retrying with a writable temporary cache succeeded. Consulted fedcourtsai.paths to resolve the owned output directory. These were path operations, not corpus queries.

## External retrieval

1. Web search query: site:supremecourt.gov Rule 10 writ certiorari erroneous factual findings misapplication properly stated rule law. Returned no usable result content.
2. Web open attempt: official Supreme Court 2023RulesoftheCourt.pdf under filingandrules. Returned no usable document content. Neither web attempt concerned this petition's disposition.
3. CourtListener MCP search: type=o, court=scotus, case_name=Mckesson v. Doe, num_results=3. Returned the November 2, 2020 decision, cluster 4802502/opinion 4582849, and a separate March 23, 2020 dismissal record. The latter was not used as a substantive analogy.
4. CourtListener MCP read_document(opinion_id=4582849): read the historical per curiam opinion, especially its discussion of certification on pages 3-5. This concerns another case and predates the provisioned record.

No fedcourts query or open-events call was made, so there are no ranged-corpus transfer lines to report. No current docket or outcome lookup for Child v. Unum was attempted.
