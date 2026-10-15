# Retrieval record

No retrieval sought this petition's disposition, subsequent history, or current docket. No files under `data/qp-topics/` or other predictors' outputs were read.

## Local context beyond provisioned case inputs

- Read the governing `AGENTS.md`, `.github/prompts/predict.md`, and prediction/tooling/flags schemas.
- Read `metrics/statpack.md`: modern discretionary-cert anchor, originating-circuit cuts, paid-segment relist/CVSG cuts, and sal-v4 reached-band table. Read corresponding Term segment entries in `metrics/statpack.json`; pooled baseline reached grants and weighted denominators for 2017–2025 with `jq`, obtaining 643 / 12,877 = 0.04993399083637493. No corpus case lookup was needed.
- `git log -1 --format='%cs %h' -- metrics/statpack.md` returned `2026-10-13 cf9ae960e`. This dates the committed artifact only.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000285 --event evt-petition-disposition --role predictor` resolved input paths. Initial execution without the cache override failed because the default uv cache was read-only.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed: the service backend has no client-side connection. No corpus rows or corpus-wide vintage were returned, and no ranged-transfer line was printed. No `fedcourts query` or `open-events` calls were made.

## Web attempts

The following `web.run` calls returned no visible content or usable results. None informed the substantive forecast:

1. Search: `site.supremecourt.gov opinions 2023 McIntosh United States 22-7386 Rule 32.2(b)(4)(B)`.
2. Search: `McIntosh United States 601 U.S. 330 2024 Supreme Court opinion footnote 5`.
3. Open the official McIntosh slip opinion at `https://www.supremecourt.gov/opinions/23pdf/22-7386_10n2.pdf`.
4. Find `harder` in that official opinion URL.

## CourtListener MCP

1. `search(type="o", citation="601 U.S. 330", num_results=3)`: located McIntosh v. United States, decided April 17, 2024. Search also returned an unrelated Court of Federal Claims result, which was not used.
2. `search_document(opinion_id=9960861, query="harder", snippet_size=1500)`: read footnote 5 and surrounding discussion. Confirmed the express reservation concerning Rule 32.2(b)(4)(B), as distinct from the preliminary-order rule.
3. `search(type="o", case_name="United States v. Skaggs", citation="78 F.4th 990", num_results=1)`: located the Seventh Circuit decision of August 23, 2023, opinion 9658456.
4. `read_document(opinion_id=9658456)`: read the returned opinion, including its disposition of a belated postjudgment preliminary forfeiture order; part of the returned text was truncated.
5. `search_document(opinion_id=9658456, query="pronouncement", snippet_size=900)`: retrieved the missing relevant discussion of the preliminary/final distinction and the conditional direct-appeal analysis.

McIntosh and Skaggs are unrelated prior litigants used as legal context. Their decided outcomes are not the outcome of the petition being forecast. The petition's other cited circuit decisions were evaluated only as described in the provisioned filing, not independently retrieved.
