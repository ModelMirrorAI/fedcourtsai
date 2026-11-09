# Retrieval record

## Local contract and inputs

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the flags/tooling schemas, `event.yaml`, `record/context.json`, `record/snapshots/2026-10-13.json`, the document manifest, questions presented, party-letter text, and selected petition sections including the complete majority disposition in its appendix. Read the paid-segment relist, CVSG, amicus and sal-v8 band sections of `metrics/statpack.md`. Did not read any realized-outcome file, another cell's prediction/evaluation, or any qp-topics artifact.

## CLI preparation and failures

- `uv run fedcourts paths --court scotus --docket 9026000396 --event evt-order-call-for-response-disposition --role predictor` initially failed because the default uv cache was read-only. No corpus result or transfer line.
- Reissued as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000396 --event evt-order-call-for-response-disposition --role predictor`; succeeded. The same successful paths command was run once more before writing. No outcome path was opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` displayed the structured-filter help.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts pdf-text --help` displayed the pinned extractor's options; no PDF extraction was performed.
- Checked whether `pdftotext` was available; it was not. No program was installed.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era roberts --limit 3`
   - Rejected the unknown era and printed valid decade tokens. No transfer line or results.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`
   - `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Returned Goldman Sachs Bank USA v. Brown (25-1408), U.S. DOGE Service v. U.S. District Court (25-1103), and Corey Duran Berry v. United States (25-7026), with grant dates in October–November 2026. This cell is forward, so the returned dates are not a replay-clock breach; the command's Term filter is not a substitute for a day cutoff. These unrelated results were not used as substantive analogues. No full opinion bodies requested.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 25-5930 --include-open --limit 1`
   - `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Returned William Maxwell v. Sandra Dinis, Acting Warden, case scotus/73281102. Granted June 1, 2026; no merits decision or judgment recorded. Confirmed the distinct related case's status described by the petition. No own-case disposition queried.

## CourtListener MCP lookups

1. `search(type="o", citation="151 F.4th 1076", num_results=2)` — zero results, query c37409a4.
2. `search(type="o", case_name="Gonzalez v. Herrera", court="ca9", num_results=3)` — located the published August 19, 2025 decision, docket 24-2371, cluster 10656685, opinion 11123272; two older name-similar unrelated results were not used.
3. `search_document(opinion_id=11123272, query="reduce", snippet_size=300)` — 27 matches, 20 shown. Confirmed that the Ninth Circuit allows earned credits to reduce supervised release and explained its conflict with contrary readings. No Supreme Court disposition of this petition appeared.
4. `search(type="o", case_name="Hargrove v. Healy", court="ca6", num_results=1)` — located the published September 10, 2025 decision, docket 24-3809, cluster 10669429, opinion 11136016.
5. `search_document(opinion_id=11136016, query="not a supervised", snippet_size=500)` — one match, confirming the holding that credits reduce a prison term but not a supervised-release term, with resulting mootness.

## Web attempts

1. One `web.run` search call with queries `site.ca9.uscourts.gov Gonzalez Herrera "151" "1076"` and `site.ca6.uscourts.gov "Hargrove" "Healy" "2025"` returned no usable content.
2. One `web.run` open call for the Ninth Circuit opinion PDF at `https://cdn.ca9.uscourts.gov/datastore/opinions/2025/08/19/24-2371.pdf` returned no usable content.

Neither web attempt supplied factual material. All independent confirmation of the conflict came from the MCP opinion searches. No search sought this petition's disposition or subsequent history, and no outcome-revealing material about it surfaced.
