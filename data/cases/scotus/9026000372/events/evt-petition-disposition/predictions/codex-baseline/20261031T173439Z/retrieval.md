# Retrieval record

## Local contract, record, and statistical context

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`. Read this cell's event, case-level context and October 31 snapshot, document manifest, questions presented, petition, relevant appendix portions, and same-question file. Checked ancestor directories for applicable `AGENTS.md` files; none were found in the checked case path. Consulted `metrics/statpack.md`, especially modern discretionary cert dispositions, originating circuit, paid-segment relist/CVSG/amicus cuts, and the `sal-v6` reached-band table. The frozen context anchor, rather than a newly computed pack-wide rate, supplies the quantitative starting point.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000372 --event evt-petition-disposition --role predictor` failed before resolving paths because `/home/codexcell/.cache/uv/CACHEDIR.TAG` was on a read-only filesystem. No case data returned and no transfer line printed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000372 --event evt-petition-disposition --role predictor` succeeded, returning the case ID, corpus locator, and event path. It labeled the outcome evaluator-only; that file was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned structured-filter syntax. Two additional help calls displayed the middle and tail sections through `sed` and `tail` because the first displayed output was truncated. These help calls made no corpus lookups and printed no transfer lines.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 4` succeeded.

   `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

   Returned four earlier-Term denials: *Google LLC v. VirtaMove, Corp., et al.* (25-1230), *Hastings College Conservation Committee, et al. v. California, et al.* (25-1231), *Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al.* (25-1098), and *Utah v. Morris Thomas Mullins* (25-1115). Each reported an October 19, 2026 denial, before this forward cell's snapshot. The filter is on docket-number Term, not an assertion that those decisions preceded calendar 2026. None is this petition, and none is a substantively matched finality precedent. No opinion bodies were requested. The deliberately denial-filtered sample was not used to estimate grant frequency.

## Web attempt

One `web.run` call attempted two general legal-context searches:

- `site.supremecourt.gov opinions 2024 Fuld Palestine Liberation Organization 24-20 June 20 2025`
- `site.govinfo.gov Calderon Thompson 523 U.S. 538 recall mandate Plaut 514 211`

The tool returned no visible result payload, quotations, or source identifiers. No fact or outcome was taken from that call. These searches targeted earlier primary authorities, not this petition's disposition or subsequent history.

## CourtListener MCP calls

1. `search(type="o", citation="606 U.S. 1", num_results=2)` returned two versions of the June 20, 2025 *Fuld v. Palestine Liberation Organization* opinion: clusters 10776827 and 10614322, opinion IDs 11243414 and 11080910. This is the earlier decision explicitly discussed in the provisioned petition and appendix, not the event being forecast. No additional search pages were retrieved.
2. `search_document(opinion_id=11080910, query="mandate", snippet_size=600)` returned one occurrence describing the earlier 2018–2019 mandate-recall proceedings. It supplied historical context only and did not decide the present question.
3. `read_document(opinion_id=11080910, chunk_index=0, chunk_size=13000)` returned the first of eleven chunks, principally the syllabus describing the statutory personal-jurisdiction holding and its foreign-policy rationale. The returned display contained an internal truncation; I did not assume any unseen text was read. No later chunk or subsequent-case treatment was requested.

No current docket was fetched, no outcome file was read, and no other predictor or evaluator output was consulted. No material revealing the disposition of petition 26-372 surfaced.
