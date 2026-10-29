# Retrieval record

## Provisioned material

Read the event definition, `record/context.json`, `record/snapshots/2026-10-01.json`, `record/documents/documents.json`, `questions-presented.txt`, and `petition.txt` including the appended lower-court decisions. A read-only independent document review used only the petition and QP, and I checked the material lower-court passages myself. No other cell's predictions/evaluations, outcome file, or QP-topic artifacts were read.

## Repository reference material

Read the predictor contract, AGENTS.md, prediction/tooling schema material, path and serialization helpers, and the relevant sections of committed `metrics/statpack.md` and `metrics/statpack.json`. An arithmetic check over JSON Term rows 2017–2025 produced 660 / 12,913 = 0.0511112832 for baseline-band reached grants. A separate read-only check reviewed this pooling and the proposed probabilities. No current corpus population count is asserted; the committed pack contains no explicit pull vintage.

## Corpus CLI attempts

- `uv run fedcourts paths --court scotus --docket 9026000223 --event evt-order-call-for-response-disposition --role predictor`: first failed because uv's default cache was read-only. Retried with `UV_CACHE_DIR=/tmp/uv-cache`; returned the case and event paths. The evaluator-only outcome was not opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`: read structured-filter usage.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 3`: refused `modern`; the CLI supplied its decade-token vocabulary. No corpus results or transfer line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`: issued the corrected query; the combined terminal display was truncated and these individual rows were not used. Its transfer/result detail was not preserved in the visible excerpt, so no transfer count is inferred for this attempt.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 2`: returned Google LLC v. VirtaMove, Corp., et al. (25-1230) and Hastings College Conservation Committee, et al. v. California, et al. (25-1231), both denied October 19, 2026. Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`. These are prior-docket-Term procedural examples, not substantive defamation analogues, and did not move my number. This cell is forward mode, so another case's decision after the snapshot date is not prohibited material; neither row concerns this petition.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info --help`: read the freshness-report contract.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`: failed because the service backend has no client-side connection. No freshness stamps or transfer line were supplied. No fallback to a local blob or credentials was attempted.

## External attempts

- Web search batch: `site.supremecourt.gov "Milkovich" "provably false"` and `site.supremecourt.gov "Berisha" "Thomas" "2021"`. No usable response content or search results were returned.
- Web open: the Cornell-hosted Milkovich opinion page (`https://www.law.cornell.edu/supct/html/89-645.ZO.html`). No usable content was returned. No quotation or legal proposition is attributed to this failed retrieval.
- CourtListener MCP `search(type="o", citation="497 U.S. 1", num_results=1)`: HTTP 429 daily rate limit; no opinion returned. No direct REST fallback was attempted.

No search requested this petition's disposition, subsequent history, or decision coverage. The legal assessment rests on pre-decision filed material and its appendix, not on the unsuccessful external lookups.
