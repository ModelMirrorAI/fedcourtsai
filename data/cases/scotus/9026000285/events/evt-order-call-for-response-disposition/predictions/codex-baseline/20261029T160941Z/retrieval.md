# Retrieval log

## Local contract and provisioned material

Read AGENTS.md, .github/prompts/predict.md, prediction and tooling schemas, the target event.yaml, record/context.json, record/snapshots/2026-09-18.json, documents.json, questions-presented.txt, and relevant petition.txt passages including the embedded First Circuit opinion at appendix 21a–23a. Read-only searches checked for applicable AGENTS.md files under data, without reading labeling artifacts or another cell's output. Local implementation reads were limited to output paths, serialization, and prediction-model requirements. No outcome file or live docket for this case was opened.

## CLI attempts and corpus retrieval

1. `uv run fedcourts paths --court scotus --docket 9026000285 --event evt-order-call-for-response-disposition --role predictor` — failed because uv's default cache was read-only. Retried with `UV_CACHE_DIR=/tmp/uv-cache`; succeeded and resolved the case/event paths.
2. `uv run fedcourts query --help` — same cache failure. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded; read the structured filter contract.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era roberts --decided-before 2026 --limit 3` — rejected: era must be a decade token. No corpus rows or transfer line returned. Corrected immediately to the documented vocabulary.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3` — succeeded. Returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. City of Chicago (25-1098), each denied October 19, 2026. The bare-year filter admits prior docket Terms, not solely dispositions before January 2026; this cell is forward and those general priors precede the October 29 run. None is this petition. These selected denied rows were used only as a reminder that multiple distributions do not guarantee review, not as an estimated base rate.

   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

5. Read committed `metrics/statpack.md`: modern cert dispositions, originating circuit, paid-segment relist, CVSG, amicus, and sal-v4 per-Term reached-band cuts. Read `metrics/statpack.json`'s matching Term segment fields; pooled 2017–2025 baseline reached values using jq, obtaining 660 / 12,913 = 0.0511112832. No own-Term row enters the anchor. The supplied pack is the vintage of these figures; it was not regenerated against the service.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` — failed because the service backend has no client-side corpus connection. No corpus-wide newest-pull or newest-snapshot stamp was returned. Did not attempt to access credentials, pull the bulk corpus, or bypass the service.

## External legal-context attempts

7. Web search: `site.supremecourt.gov opinions McIntosh United States 2024 Rule 32.2(b)(4)(B) expressly declined` — tool returned no usable source content or source identifier. No own-case disposition was sought or surfaced in the returned content.
8. CourtListener MCP `search`, type `o`, case_name `United States v. Harrell`, court `ca6`, filed_after `2026-07-01`, filed_before `2026-07-04`, num_results `3` — HTTP 429, daily rate limit exceeded. No opinion content returned. No CourtListener REST fallback attempted.
9. Web open of the official McIntosh opinion URL `https://www.supremecourt.gov/opinions/23pdf/22-7386_7k47.pdf` — tool returned no usable document content or source identifier. No external holding was inferred from this unsuccessful request.

The legal assessment ultimately relies on the staged petition and its embedded pre-petition appellate opinion. No usable external source added case-specific facts, and no known outcome-revealing information about this petition was encountered.
