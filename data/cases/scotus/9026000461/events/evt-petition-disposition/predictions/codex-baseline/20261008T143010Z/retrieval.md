# Retrieval record

## Provisioned and repository inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas.
- Read this cell's event, `record/context.json`, `record/snapshots/2026-10-08.json`, and both provisioned document files. The petition text is unavailable as its manifest declares.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist/CVSG cuts, and the sal-v4 segment table. Computed the private baseline reached anchor from its displayed 2017–2025 rows, approximately 5.01% over weighted n=12,720. No other cell's prediction or realized outcome was consulted.
- Ran `uv run fedcourts paths --court scotus --docket 9026000461 --event evt-petition-disposition --role predictor`. The first attempt failed on an unwritable default cache; a retry using a temporary cache succeeded. This resolves paths and does not query the corpus. No `fedcourts query` or `open-events` lookup was made, and no ranged-corpus transfer line was emitted.

## Web

- Attempted `web.open` on the exact Supreme Court petition PDF URL in the document manifest, ending `20261007122400796_Petition.Herridge.pdf`. The tool returned no readable content. No search for this petition's disposition or later history was performed.

## CourtListener MCP

1. `search(type="o", q='"Herridge" "Chen"', court="cadc", filed_after="2025-09-29", filed_before="2026-05-23", num_results=5)`. Returned one antecedent D.C. Circuit decision: *Yanping Chen v. FBI*, No. 24-5050, filed September 30, 2025; cluster 10681709, opinion 11148296. The search was confined to the lower court and dates preceding this petition's filing.
2. `read_document(opinion_id=11148296, chunk_index=[0,1,2], chunk_size=11000)`. Retrieved the opinion's three chunks; the display truncated portions, so I did not treat unshown material as read.
3. `search_document(opinion_id=11148296, query="III", snippet_size=2800)`. Read the procedural history, contempt order, appealability discussion, and opening privilege analysis around section III. Together with the visible beginning and conclusion of the full-document response, this supplied the substantive basis used in the forecast.

No Supreme Court disposition, post-petition case history, labeling-measurement artifacts, or evaluator-only material was retrieved.
