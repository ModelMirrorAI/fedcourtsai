# Retrieval record

## Local inputs and reference material

Read `.github/prompts/predict.md`, the prediction and tooling schemas, the event definition, the case-level `record/context.json`, `record/snapshots/2026-11-08.json`, the document manifest, questions presented, and the relevant petition/appendix and opposition text. Read `metrics/statpack.md`, including modern-cert disposition, circuit, relist, CVSG, amicus, capital, and sal-v8 reached-rate sections. No other cell's output or evaluator outcome was read.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000353 --event evt-petition-disposition --role predictor` — failed initializing the default uv cache on a read-only filesystem; no case retrieval occurred.
2. `uv run fedcourts query --help` — same cache failure; no corpus query occurred.
3. `UV_NO_CACHE=1 uv run fedcourts query --help` — succeeded; read structured-filter documentation. Repeated once with output limited to its tail to inspect options. Neither help call retrieved priors.
4. `UV_NO_CACHE=1 uv run fedcourts paths --court scotus --docket 9026000353 --event evt-petition-disposition --role predictor` — succeeded; resolved case, corpus, and event paths and withheld the evaluator-only outcome path. Repeated once for a clean visible path listing. No outcome was opened.
5. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026-11-08 --limit 3` — returned Scanlan v. Coalition for Open Democracy (26A512, a substantive application), Association for Education Fairness v. Montgomery County Board of Education (26-12), and Department of Justice v. McNutt (26-204). The last two had respectively three and two distributions. No subject-matter matching or opinion hydration was requested. The date screen was a precaution on a forward cell, not a replay-mode classification. These grant-selected records were not used to estimate a grant rate.

   `ranged corpus reads: 22 GET(s), 5767168 byte(s)`

6. `UV_NO_CACHE=1 uv run fedcourts query --court scotus --citation '142 S. Ct. 2576' --limit 2` — no result. The CLI warned that only 200 scoped rows carry reporter citations and that missing citation coverage is more likely than nonexistence of the case. No further sparse-filter retries.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## Web attempts

1. One `web.run` search call containing `site.supremecourt.gov Storey Lumpkin 2022 Sotomayor Brady successive` and `site.supremecourt.gov Bowe 2244(b)(3)(E) 607 2026` — returned no visible results or source text. No inference drawn.
2. One `web.run` search call for `"Storey v. Lumpkin" "Sotomayor" "2022"` — likewise returned no visible results or source text. No inference drawn. Neither search targeted Vasquez or this petition's disposition.

## CourtListener MCP

1. `search(type="o", q='caseName:"Storey v. Lumpkin"', num_results=3)` — one result: Fifth Circuit, August 6, 2021, lead docket 20-70017, cluster 4906045, opinion 4709824. This was a different litigant's precedent, not the target case. Result path: `/opinion/4906045/storey-v-lumpkin/`.
2. `search_document(opinion_id=4709824, query="successive", snippet_size=600)` — 46 matches, first 20 displayed; identified discussion of transfer, authorization, and successive habeas petitions.
3. `read_document(opinion_id=4709824, chunk_index=5, chunk_size=7000)` — read the section beginning at the discussion of whether transfer of Storey's new federal habeas petition was proper, including authorization, Panetti, and Magwood context. It does not supply this case's outcome or a Supreme Court ruling on the question presented. Primary opinion location returned by MCP: `http://www.ca5.uscourts.gov/opinions/pub/20/20-70017-CV0.pdf`; no separate fetch of that PDF was made.

## Validation

The required cell-specific validator is run after writing these files with `UV_NO_CACHE=1`; it is a local output check, not retrieval of an evaluator outcome.
