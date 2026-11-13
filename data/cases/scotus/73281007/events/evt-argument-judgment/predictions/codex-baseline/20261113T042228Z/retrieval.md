# Retrieval record

All case-specific merits evidence came from the provisioned case-level record. No live query sought this case's disposition, subsequent history, commentary, or another forecast. No prediction or evaluation output from another cell was read.

## Corpus calls

The default uv cache was unwritable, so successful CLI invocations used `UV_CACHE_DIR=/tmp/uv-cache`. No packages were installed.

1. `uv run fedcourts paths --court scotus --docket 73281007 --event evt-argument-judgment --role predictor` initially failed before resolving paths because `/home/codexcell/.cache/uv` was read-only. Reissued with the temporary cache setting; it returned the case identifier, corpus path, event path, and an evaluator-only outcome placeholder, not outcome content. The same successful path-resolution command was run once again near completion. These were local path lookups, not corpus record retrievals, and printed no ranged-read statistics.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` was consulted before the first query. Subsequent views of the same help output used `head -55` and `sed -n '1,37p'` to recover the truncated option descriptions. Help made no corpus lookup and printed no ranged-read statistics.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '603 U.S. 109' --limit 3` returned no matching rows and explained sparse citation coverage: only 195 scoped SCOTUS rows had reporter citations. Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. An empty result was not treated as absence of Jarkesy.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 22-859 --limit 1` successfully identified **Securities and Exchange Commission v. George R. Jarkesy, Jr., et al.**, `scotus/68045400`. Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. This metadata lookup did not hydrate the opinion body.

## CourtListener MCP

5. `search(type="o", citation="603 U.S. 109", num_results=1)` returned Jarkesy, June 27, 2024, docket 22-859, cluster **10600046**, combined opinion **11066634**, attributed to Roberts. The result verified the precedent's identity; no subsequent citing case was opened.
6. `search_document(opinion_id=11066634, query="immigration", snippet_size=1800)` returned 16 matching excerpts from Jarkesy, including the majority's discussion preserving historic public-rights categories and immigration penalties, and passages from separate writings. This supplied the external doctrinal check used in the rationale. No document from the forecast case was retrieved through MCP.

## Web attempts

The web tool produced no visible result content or usable source references for these calls. They supplied no additional evidence and no case outcome or forecast was surfaced:

7. Combined search queries: `site.supremecourt.gov "Jarkesy" "603" "109" public rights immigration Oceanic` and `site.supremecourt.gov "Oceanic Steam" "214" "320"`.
8. Search query: `SEC v Jarkesy 2024 Supreme Court opinion public rights immigration 22-859`.
9. Open attempt: `https://www.supremecourt.gov/opinions/23pdf/22-859_1924.pdf`.

## Committed reference material and calculations

Consulted `metrics/statpack.md`'s merits, per-Justice vote, and coverage captions; `metrics/statpack.json`'s `merits`, `justice_votes`, and `authorship` blocks; and the relevant merits-cohort and coverage explanations in `metrics/README.md`. Only strictly pre-OT2025 rows were used for the forecast's historical counts. Local calculations pooled 2015–2024 grant-Term merits rows and pre-2025 vote/authorship rows. No corpus-wide statistics command or additional remote data retrieval was attempted. Schema reads, input inspection, and cell validation are local workflow operations, not substantive external retrieval.
