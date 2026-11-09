# Retrieval beyond provisioned inputs

No lookup sought this petition's disposition or subsequent history. The case's own Supreme Court docket was read only from the provisioned snapshot. General precedent and a different granted case were consulted in forward mode.

## Local reference material and CLI discovery

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and the tooling/flags schemas. Checked for applicable `AGENTS.md` files; none were found.
- Read the relevant cert sections of `metrics/statpack.md` and selected aggregate structures in `metrics/statpack.json`. Computed the strictly-prior federal reached pool (155/212) and the one-or-more-relist cross-check (726/3,510). No case-level outcome artifact was opened.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000239 --event evt-order-relist-disposition --role predictor`; the default uv cache was read-only, so the command failed before path resolution. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000239 --event evt-order-relist-disposition --role predictor`. The evaluator-only outcome path was not read.
- Consulted `fedcourts query --help` three times, with output formatting/filtering on the latter calls, and `fedcourts open-events --help` once. These were discovery calls, not corpus queries. All successful CLI invocations used `UV_CACHE_DIR=/tmp/uv-cache` and `uv run --no-sync`; no package was installed.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 17-965 --limit 1`
   - Returned Trump v. Hawaii, case `scotus/6375111`. Long attorney metadata made the combined tool display truncate; a compact verification followed below.
   - `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 26-426 --include-open --limit 1`
   - Attempted in the same shell call as lookup 1; the combined displayed response was truncated, so its transfer line was not available in the displayed excerpt. Reissued immediately with a compact stdout projection, below. No numerical transfer count is invented for this first attempt.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 26-426 --include-open --limit 1` (stdout projected to selected fields)
   - Returned DHS v. D.V.D., case `scotus/9026000426`, filed September 29, 2026, disposition `granted`, no opinion body. Not this cell's case.
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 17-965 --limit 1` (stdout projected to selected fields)
   - Confirmed the historical Hawaii petition's `granted` disposition and one distribution. No opinion body requested.
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`

## CourtListener MCP

- `search(type="o", citation="596 U.S. 543", num_results=1)`: returned Garland v. Gonzalez / Garland v. Aleman Gonzalez, decided June 13, 2022, docket 20-322, cluster 6477116, combined opinion 6349227. The result supplied the official Supreme Court PDF address. No additional MCP endpoint, document-read, or citation-analysis call was made.

## Web retrieval

- Search call with two queries: `site.supremecourt.gov opinions 2021 Garland Aleman Gonzalez 1252(f)(1) 20-322` and `site.supremecourt.gov opinions Trump Hawaii 17-965 1182(f)`. Sought primary-source general precedent, not either litigant's current case disposition. No readable tool-response payload was available; no reliance on search hits.
- Attempted opening `https://www.supremecourt.gov/opinions/21pdf/20-322_new_986b.pdf`; no readable tool-response payload was available. Not relied on.
- Attempted opening `https://www.supremecourt.gov/opinions/17pdf/17-965_h315.pdf?os=___`; no readable tool-response payload was available. The historical corpus row and staged filings supplied the limited Hawaii analogy.
- Attempted opening `https://www.supremecourt.gov/opinions/21pdf/20-322_m6hn.pdf`, the official Aleman Gonzalez address supplied by CourtListener. No readable tool-response payload was available. The discussion of this precedent rests on the provisioned filings and the MCP identity check, not an independent opinion reading.
- Attempted opening `https://www.supremecourt.gov/docket/docketfiles/html/public/26-426.html`, the official docket of the separate DHS v. D.V.D. case. No readable tool-response payload was available. The corpus independently verified only its grant; the stated Section 1252(f)(1) overlap and December 9 argument schedule derive from the staged reply, page 12. No grant date, precise granted-question wording, or companion holding is inferred from this unsuccessful read.

The provisioned filing text was summarized rather than reproduced. No source beyond those listed was used; no other prediction, evaluation, realized outcome, or `data/qp-topics/` material was consulted.
