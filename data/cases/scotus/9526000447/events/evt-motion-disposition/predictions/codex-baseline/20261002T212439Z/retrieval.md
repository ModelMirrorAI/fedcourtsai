# Retrieval record

## Provisioned inputs

Read the cell's event.yaml, record/context.json, record/snapshots/2026-10-01.json, record/documents/documents.json, and relevant portions of record/documents/application.txt. Case-specific factual analysis uses only these materials. No outcome, current docket, subsequent history, other predictor output, or labeling artifact was read.

## Local context

- Read AGENTS.md, .github/prompts/predict.md, and the prediction, tooling, and flags schemas for the output contract.
- Ran `uv run fedcourts paths --court scotus --docket 9526000447 --event evt-motion-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; the retry with a writable temporary cache succeeded. This was path resolution, not a corpus lookup.
- Read the interim section of metrics/statpack.md and the corresponding metrics/statpack.json structure. Used jq to sum substantive resolutions and grants for application-Terms 2016–2025: 296 and 31, yielding 0.10472972972972973. No live corpus lookup occurred and no ranged-corpus transfer line was emitted.

## Web attempts: historical precedents only

- Search query: `site.supremecourt.gov Hollingsworth Perry 558 U.S. 183 stay reasonable probability fair prospect`.
- Search query: `site.loc.gov Fisher District Court 424 U.S. 382 1976 final original proceedings`.
- Attempted to open the Library of Congress U.S. Reports PDF for Fisher, volume 424, page 382. The tool returned no usable content for the searches or the open. None contributed substantive evidence or case-outcome information.

## CourtListener MCP

1. `search(type="o", citation="558 U.S. 183", num_results=2)`: located Hollingsworth v. Perry, January 13, 2010; also returned an irrelevant lower-court result, which I did not use.
2. `search_document(opinion_id=9413203, query="reasonable probability", snippet_size=900)`: verified the stay standard at 558 U.S. 190.
3. `search(type="o", q="\"Fisher v. District Court\"", court="scotus", filed_before="1977-01-01", filed_after="1976-01-01", num_results=1, fields=["caseName","citation","opinions","absolute_url"])`: located Fisher, March 1, 1976, opinion 109385.
4. `search_document(opinion_id=109385, query="terminates", snippet_size=650)`: verified the original-proceeding finality language, including its lower-court-jurisdiction qualification.

No direct CourtListener REST calls, live corpus queries, or searches about Swift's disposition were made.
