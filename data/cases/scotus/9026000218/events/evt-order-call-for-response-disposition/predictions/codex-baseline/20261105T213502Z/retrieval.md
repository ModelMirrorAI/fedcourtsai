# Retrieval record

## Provisioned inputs and local context

Read the contract, prediction schema, event definition, `record/context.json`, `record/snapshots/2026-09-30.json`, document manifest, questions presented, the substantive petition sections, the appendix's opening lower-court decisions, and `record/same-question.json`. Read the required output schemas. Local non-case context: `metrics/statpack.md`, particularly its paid scored-segment relist, CVSG and amicus cuts and prior-Term salience table; inspected the top-level structure of `metrics/statpack.json`. No other prediction or outcome file was read.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000218 --event evt-order-call-for-response-disposition --role predictor` failed before running the CLI because the default uv cache was read-only. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; it returned the expected case and event paths and described the outcome as evaluator-only. No outcome path was opened.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned the structured-filter documentation. The beginning was subsequently displayed again to inspect the filter names.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition granted --decided-before 2026 --limit 5` was refused: `modern` is not a valid era token. The error supplied the decade vocabulary. No corpus results or transfer line were returned.
4. Corrected lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --decided-before 2026 --limit 5`. Initially silent during status checks; eventually completed with exit code 0 and no matching case rows. Exact stderr transfer report: `ranged corpus reads: 997 GET(s), 261160960 byte(s)`. No retrieved prior was used. The shell command also displayed the already-consulted local statpack sections after the query finished.
5. Narrow precedent lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '577 U.S. 385' --decided-before 2026 --limit 2`. Eventually completed with exit code 0 and no matching case rows. Exact stderr transfer report: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`. It warned that only 200 in-scope SCOTUS rows carried any reporter citation, and that absence therefore more likely reflects missing metadata than a nonexistent case. CourtListener independently supplied the comparator.

The queries' empty results are not evidence that historical comparators do not exist. Both valid queries concern historical context, not this petition. While waiting for output checks, inspected the local CLI validation implementation and corpus-service timeout constant, with no substantive case or outcome retrieval. Validation is run separately with the required cell path and the temporary-cache environment setting; it is an output check, not substantive retrieval. The first completed validation reported `OK: 29869 artifact(s) valid, 71184 reference(s) consistent; cell complete`. It is repeated after these retrieval-log updates.

## CourtListener MCP

1. `search(type="o", citation="577 U.S. 385", court="scotus", num_results=2)` returned Wearry v. Cain, filed March 7, 2016, docket 14-10008, cluster 3183098, opinion 3183080.
2. `read_document(opinion_id=3183080, chunk_index=[0,1], chunk_size=9000)` returned the beginning of that historical opinion and its account of the suppressed evidence and materiality analysis. The opening identifies the reversal of the Louisiana postconviction judgment.
3. `search_document(opinion_id=3183080, query="ALITO", snippet_size=1000)` returned the disposition granting certiorari, reversing and remanding, followed by Alito's dissent joined by Thomas. Used to verify the summary-correction route and not as a statistical grant-rate estimate.

## Web tool attempts

1. One search call contained `site.supremecourt.gov opinions Wearry Cain 14-10008 Brady 2016` and `site.supremecourt.gov opinions Turner United States 16-471 Brady 2017`. It returned no visible result payload. No search result was used.
2. An open call attempted the official Wearry opinion at `https://www.supremecourt.gov/opinions/15pdf/14-10008_k537.pdf`. It returned no visible result payload; the CourtListener text, not this attempt, supplied the precedent.

No own-case live docket, own-case outcome, subsequent-history search, or direct CourtListener REST request was attempted.
