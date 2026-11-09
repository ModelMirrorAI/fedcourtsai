# Retrieval record

## Local reference and setup calls

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; inspected required fields with `jq`. An initial `jq` expression using `.$defs` failed to compile; corrected to `."$defs"`. These are contract/schema reads, not case retrieval.
- Ran `uv run fedcourts paths --court scotus --docket 9026000602 --event evt-petition-arrival-disposition --role predictor`. First attempt failed because the default uv cache was read-only. Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000602 --event evt-petition-arrival-disposition --role predictor`, successfully resolving the case and event paths.
- Read the committed `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist/CVSG/amicus cuts, and prior-Term sal-v8 reached bands. No aggregate-statistics command or package installation was used.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`, then repeated that help command with output restricted to its opening 65 lines while selecting valid filters.

## Corpus calls

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era roberts --decided-before 2026 --limit 3`
   - Refused: `roberts` is not an era token; the command printed the valid decade vocabulary. No ranged-read transfer line was printed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`
   - Succeeded; returned Robert J. Jesenik v. United States (25-7515), Andrew N. MacRitchie v. United States (25-7522), and Tauno Waidla v. Christopher Pierce (25-7555), all denial examples, with no opinion bodies. These are broad modern comparators, not bankruptcy analogues. The command's year filter is not a strict decision-date filter; returned denial dates were November 9, 2026. This is legitimate forward general context, not this case's outcome, and none was used to estimate a numerical base rate.
   - Exact stderr transfer report: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`.

## Web calls

Both calls returned no usable result body, URLs, or citation references; no web result influenced the prediction.

1. `web.run`, three search queries:
   - `site.supremecourt.gov Taggart Lorenzen 2019 18-489 opinion`
   - `site.uscode.house.gov 11 USC 362 action proceeding against debtor`
   - `site.supremecourt.gov Rules Rule 10 error correction certiorari`
2. `web.run`, two search queries:
   - `Taggart v Lorenzen 2019 Supreme Court opinion no fair ground doubt`
   - `11 USC 362 debtor plaintiff action automatic stay`

## CourtListener MCP calls

1. `search(type="o", court="scotus", citation="587 U.S. 554", num_results=1)` returned *Taggart v. Lorenzen*, June 3, 2019; cluster 4625564, opinion 4402817, docket 18-489. Used only as legal precedent, not as an analogue for this petition's grant odds.
2. `search_document(opinion_id=4402817, query="automatic stay", snippet_size=600)` returned six snippets distinguishing automatic-stay remedies and purposes from discharge-order contempt.
3. `search_document(opinion_id=4402817, query="no fair ground of doubt", snippet_size=260)` returned the objective standard for civil contempt for a discharge-order violation.

No own-case disposition search, companion-case search, live docket retrieval, opinion-body corpus hydration, or access to other predictions/evaluations was attempted. Provisioned filings and snapshots were consulted directly, not retrieved externally. The required cell validator is run separately as a local output check.
