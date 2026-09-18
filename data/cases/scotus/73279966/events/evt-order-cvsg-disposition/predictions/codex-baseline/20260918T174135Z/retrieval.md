# Retrieval record

## Provisioned inputs

Read the event definition, May 19, 2026 snapshot, context, document manifest, questions presented, and relevant portions of the petition and both combined opposition briefs. No target-case outcome, other prediction, or later target docket was retrieved.

## Additional local sources

- `metrics/statpack.md`: paid-segment relist and CVSG cuts and the sal-v4 per-Term reached-rate table.
- `metrics/statpack.json`: exact high-band reached rates and weighted denominators for the table's prior Terms, 2017–2024. A `jq` aggregation returned 314 / 898 = 0.34966592427616927.
- Task/schema and serialization tooling only: prediction, agent flags, and agent tooling schemas; `fedcourtsai.serialize` helpers.
- `uv run fedcourts paths --court scotus --docket 73279966 --event evt-order-cvsg-disposition --role predictor`: initial attempt failed because the default uv cache was read-only; rerunning with a writable cache resolved the paths. The evaluator-only outcome was not opened.
- No `fedcourts query` or `open-events` calls; consequently no ranged corpus-read transfer lines.

## Web attempts

1. `web.run` search query: `site.supremecourt.gov Rule 10 considerations governing review certiorari`. No usable result was returned.
2. `web.run` open of the Supreme Court's `filingandrules/2026rulesofthecourt_web.pdf` endpoint. No usable content was returned; no rule text was relied upon.

Neither attempt searched this petition or its outcome.

## CourtListener MCP

1. `search(type="o", citation="145 F.4th 315", num_results=2)`: zero results.
2. `search(type="o", case_name="CoreCivic", court="ca3", filed_before="2026-01-09", num_results=3)`: one result, **CoreCivic Inc. v. Governor of New Jersey**, No. 23-2598, filed July 22, 2025; cluster 10638669, opinion 11105256. The search was restricted to opinions before the target petition's filing.
3. `search_document(opinion_id=11105256, query="Nwauzor", snippet_size=2000)`: one match, showing slip-opinion pages 24–25. The majority distinguishes neutral conditions on contractors from a ban on federal detention contracting and leaves the former questions open. Used to evaluate the claimed circuit conflict, not to infer any later disposition of the target case.

No live target-case MCP lookup was made. No outcome-revealing information was encountered.
