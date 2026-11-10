# Retrieval record

## Provisioned and committed local sources

Read the prediction contract and prediction/flags/tooling schemas; the event definition; the case-level context and November 9, 2026 snapshot; document inventory; questions presented; petition and its bound district-court and rehearing orders; provisioned decision below and lower-court docket summary; and same-question metadata. Read `metrics/statpack.md`, particularly the modern-cert, circuit, paid-segment relist/CVSG/amicus, and sal-v8 prior-Term reached-band sections. No other cell's output or outcome record was read.

## CLI and corpus calls

Commands below were run from the repository root. The first paths command used the default cache; subsequent uv commands used `UV_CACHE_DIR=/tmp/uv-cache` after that cache proved read-only. No package-install command was run.

1. `uv run fedcourts paths --court scotus --docket 9026000355 --event evt-petition-disposition --role predictor` failed before retrieval: default uv cache at `/home/codexcell/.cache/uv` was read-only.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000355 --event evt-petition-disposition --role predictor` succeeded and confirmed case/event paths. The evaluator-only outcome was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` read the structured-filter interface. A second help invocation, piped through `head -75`, reviewed those filters. Neither is a corpus lookup.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '513 U.S. 219' --limit 2` attempted to locate *American Airlines v. Wolens*. No matching prior was usable; the terminal output of this first invocation was clipped in a combined read. Its individual transfer line was not retained in the visible output, so I repeated the lookup separately rather than inferring its contents or transfer.
5. The identical citation query was repeated. It returned no rows and explained that only 200 SCOTUS rows in scope carried reporter citations; an empty result is a coverage gap, not absence of the precedent. Its exact stderr transfer line was:

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2010s --limit 3` returned three resolved historical grants: *Johnson v. Arteaga-Martinez* (19-896), *Hughes v. Northwestern University* (19-1401), and *Dobbs v. Jackson Women's Health Organization* (19-1392). The full combined terminal output was clipped, so I subsequently requested compact field projection. This grant-selected sample is not an airline-preemption analogue or a grant-rate denominator and did not drive the numerical update. Its exact transfer line was:

   `ranged corpus reads: 274 GET(s), 71827456 byte(s)`

7. The same three-prior query was repeated with output piped to `jq -c '{case_id,case_name,docket_number,date_cert_granted,disposition,distribution_count,cvsg_date,has_opinion}'`. This confirmed the three captions above, distribution counts of 3, 3, and 22, and a CVSG only for Hughes; none carried an opinion body. The repeat was not transfer-free. Exact stderr:

   `ranged corpus reads: 268 GET(s), 70254592 byte(s)`

The forward context has no replay clock and no `decided_before` value; these historical-prior calls did not seek the subject petition. No `--full` opinion hydration or `open-events` call was made.

## CourtListener MCP

- `search(type="o", court="scotus", citation="572 U.S. 273", num_results=1)` attempted to verify *Northwest, Inc. v. Ginsberg*. It returned HTTP 429, reporting the 25/minute upstream rate limit and an expected 24-second wait. I did not retry or use direct REST. The forecast instead uses the provisioned petition's account, expressly identified as such.

## Web attempts

One web search call submitted both general-precedent queries:

- `site.supremecourt.gov opinions Northwest Ginsberg 2014 12-462 service preemption`
- `site.supremecourt.gov opinions "Dan’s City" "removal" "transportation"`

The web tool returned no usable result content. A subsequent open attempted the official Supreme Court Ginsberg opinion, docket 12-462, filename `12-462_p09r.pdf` under its 2013-Term opinions path; that also returned no usable content. No holding, quotation, or fact from those attempts is relied upon. No query sought this petition's own outcome, subsequent history, or coverage.

## Validation

The final cell is checked with the contract's `uv run fedcourts validate data --cell` command, using the same temporary uv-cache override. Validation is a local output check, not additional case retrieval.
