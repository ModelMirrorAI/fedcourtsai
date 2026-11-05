# Retrieval record

## Local inputs and reference material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; the event definition; the case-level context, November 5 snapshot, document manifest, and same-question list; questions presented, petition, lower-court decision and docket synopsis; and relevant portions of the appendix. Consulted `metrics/statpack.md`, including the sal-v6 reached-band table and paid-segment relist, CVSG, and amicus cuts. These are local reference/input reads, not searches for an outcome. No prediction or evaluation tree other than this cell's own output was read.

## Tooling and corpus requests

1. `uv run fedcourts paths --court scotus --docket 9026000527 --event evt-petition-disposition --role predictor` failed because the default uv cache directory was read-only. No case data were returned by that attempt.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000527 --event evt-petition-disposition --role predictor` succeeded and resolved the case and event paths. The outcome path was withheld as evaluator-only. No packages were installed.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned the structured-filter interface. A second help request, `UV_CACHE_DIR=/tmp/uv-cache COLUMNS=140 uv run fedcourts query --help`, displayed the wider option descriptions. Neither retrieved corpus rows or printed a transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 4` returned Google LLC v. VirtaMove, Corp., et al. (25-1230; two distributions), Hastings College Conservation Committee, et al. v. California, et al. (25-1231; two), Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al. (25-1098; four), and Utah v. Morris Thomas Mullins (25-1115; three). All four returned cert-denial dates were October 19, 2026, before this forecast. The year mask is a derived-Term filter, not a guarantee of calendar dates before January 1, 2026. These are selected negative procedural examples, not a frequency estimate and not established trademark analogues. No full opinion bodies were requested.

   Exact stderr transfer line: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`.

## Web attempts

The web tool returned no usable result text or source handles for the following requests. None supplied facts used in the prediction; no request concerned this petition's disposition.

1. One `web.run` search call containing both queries: `site.supremecourt.gov opinions 2014 B&B Hardware 13-352 pdf materially same` and `site.supremecourt.gov rules Rule 10 error correction judicial proceedings`.
2. `web.run` open of `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
3. `web.run` open of `https://www.govinfo.gov/content/pkg/USREPORTS-575/pdf/USREPORTS-575-138.pdf`.

## CourtListener MCP

1. `search(type="o", citation="575 U.S. 138", num_results=2)` succeeded, query id `af99af59`. It returned historical B&B Hardware clusters 2959751 and 2788685, dated March 24, 2015. The first result identified lead opinion 9812717 and concurrence 9812718. Its concurrence snippet emphasized the limited application of preclusion where registration proceedings compare marks without their marketplace uses. This confirmed the relevance of the precedent; the provisioned record remained the substantive source.
2. `search_document(opinion_id=9812717, query="materially the same", snippet_size=2000)` failed with HTTP 502. No opinion-text passage was returned. Following the contract's degradation rule, I relied on the provisioned record and corpus/statpack and did not attempt a direct CourtListener REST fallback.

## Boundary and exclusions

This is a forward cell with no retrieval cutoff. I nevertheless limited the corpus examples to an earlier docket-Term cohort. I did not search for this case on the web or retrieve its current disposition, later history, another predictor's outputs, evaluation material, or topic-label artifacts. No outcome-revealing information surfaced. Validation is a local schema/completeness check, not an additional retrieval.
