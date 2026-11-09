# Retrieval log

## Baseline and local context

Read the prediction contract and schema, event definition, case-level November 9 snapshot, document manifest, questions presented, petition, lower-court docket summary, context, related.json, both Vide snapshots, and same-question.json. Consulted the committed `metrics/statpack.md`, especially prior-Term sal-v8 reached rates and the relist, CVSG, circuit and amicus cuts. No other cell's local outputs, evaluator outcomes, or topic-label artifacts were read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000294 --event evt-order-relist-disposition --role predictor` failed before resolving paths: default uv cache was read-only.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000294 --event evt-order-relist-disposition --role predictor` succeeded. The outcome was identified only as evaluator-only; it was not read.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` was read; two later calls displayed portions of the same help text to inspect available flags. No retrieval was made by those help calls.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 4` returned recent granted rows. This was a broad procedural sanity check, not a matched FSIA sample or a grant-rate estimator. Its returned population included a substantive application, which was excluded from cert reasoning.

   `ranged corpus reads: 31 GET(s), 8126464 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '560 U.S. 305' --limit 2` returned no rows. The CLI warned that only 200 SCOTUS rows carried reporter citations; the result was treated as a coverage limitation, not negative legal evidence. The shell projected selected fields with jq if rows existed.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

The context is forward and decided_before is null, so no replay clock was required. No packages were installed.

## CourtListener MCP

1. `search(type="o", citation="73 F.4th 157", num_results=2)` returned OI European Group BV v. Bolivarian Republic of Venezuela, Third Circuit, July 7, 2023, cluster 9412117, opinion 9407593. Used to identify the cited analogy, not this petition's outcome.
2. `search_document(opinion_id=9407593, query="recognition", snippet_size=650)` returned two snippets, including the competing Venezuelan governments and PDVSA relationship. This corroborated the analogy's different factual setting; it was not a full-opinion review.

## Web calls

1. One two-query search requested `site.supremecourt.gov opinions Zivotofsky Kerry 2015 recognition sovereign immunity` and `site.supremecourt.gov opinions 2026 Exxon Mobil Corporacion Cimex sovereign immunity`. No usable displayed material was taken from the returned response.
2. Opened the already-filed Faiq PDF URL below; the initial response supplied no usable displayed material.
3. A find request on that URL for `Owens` likewise supplied no usable displayed material.
4. Opened `https://www2.ca3.uscourts.gov/opinarch/231647p.pdf`; no usable displayed material was taken from that response. The later MCP snippets, rather than an assumed reading of the PDF, were used.
5. Searched `"Faiq" "26-294"` to locate the existing opposing filing. The results included the official PDF and incidental external prediction-page snippets. Those forecast pages were not opened and their predictions were disregarded; see flags.json. No search was directed at a decision or subsequent history.
6. Reopened the official Faiq PDF successfully and read its opposition arguments, particularly printed pp. 8–19. It was filed October 5, 2026, before the baseline; no later docket state was retrieved.

Official filed brief URL: `https://www.supremecourt.gov/DocketPDF/26/26-294/428540/20261005174238426_Faiq%20cert%20op%20%20-%20final%20to%20printer.pdf`.

All reliance on the amicus is identified as an adversary's position. No CourtListener REST fallback, live own-case disposition query, or own-case outcome material was used.
