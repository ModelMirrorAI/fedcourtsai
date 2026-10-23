# Retrieval log

## Local context beyond the provisioned case inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction and tooling JSON schemas, and the relevant path, ID, serialization, and prediction-model definitions to satisfy the output contract.
- Read only the merits section of `metrics/statpack.md` and the corresponding `merits` object of `metrics/statpack.json`. An executed Python sum selected `2015 <= term < 2025`, obtaining 360 disturbed / 516 parsed, 539 granted, and 56 separately excluded. No live corpus freshness claim is attached to this committed pack.
- `uv run fedcourts paths --court scotus --docket 73282277 --event evt-order-judgment --role predictor` initially failed because the default uv cache was read-only. Repeated successfully with `UV_CACHE_DIR=/tmp/uv-cache`. This resolved paths only, not corpus contents or the outcome.
- No `fedcourts query`, `open-events`, corpus pull, or own-case historical lookup was made. There are no ranged-corpus transfer lines to report.

## CourtListener MCP

- `search(type="o", citation="590 U.S. 83", num_results=1)` sought the general Ramos v. Louisiana precedent, not this case. It returned HTTP 429, with a 300/hour limit and approximately 2,270 seconds until availability. No opinion text was returned. No direct REST fallback was attempted.

## Web attempts

The following general-precedent searches were attempted, in order. The web interface returned no usable source text for these calls, so no search result or opinion body was relied upon:

1. `site.supremecourt.gov Khorrami Arizona 2022 Gorsuch Kavanaugh twelve jury Williams`
2. `site.supremecourt.gov Ramos Louisiana 19 110 2020 opinion jury Kavanaugh Roberts Alito`
3. `site.supremecourt.gov opinions "Cunningham" "23–5171" Gorsuch 2024`
4. `Sullivan Louisiana 508 U.S. 275 jury structural error harmless error hypothetical jury`
5. `Khorrami Arizona Gorsuch Kavanaugh November 7 2022 twelve jurors`
6. `site.supremecourt.gov "Ramos" "18-5924" "2020" opinion`
7. `site.law.cornell.edu "Sullivan" "hypothetical jury" "275"`
8. Attempted to open the general Ramos opinion at `https://www.supremecourt.gov/opinions/19pdf/18-5924_n6io.pdf`; no usable content was returned.

No search requested Hamed Kian's disposition, later proceedings, or decision coverage. No own-case outcome or post-grant merits material was retrieved. The legal authorities used in the reasoning are those discussed in the provisioned briefs and appendix, together with general legal knowledge, not newly retrieved opinion text.
