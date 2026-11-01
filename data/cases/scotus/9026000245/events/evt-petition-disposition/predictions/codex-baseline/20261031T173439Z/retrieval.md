# Retrieval log

## Local contract, record, and baseline material

Read `.github/prompts/predict.md`, the prediction, tooling, and flag schemas, the event definition, `record/context.json`, `record/snapshots/2026-10-31.json`, the documents manifest, questions presented, relevant petition/opposition/reply/appendix passages, and `record/same-question.json`. Consulted the committed `metrics/statpack.md`, particularly the paid relist, CVSG, amicus, circuit, and sal-v6 prior-Term reached-band cuts. Local file discovery, line searches, schema projections, and working-tree status checks did not retrieve external case evidence. Some large command outputs were truncated by the tool renderer; focused follow-up reads supplied the passages used in the forecast. No other prediction, evaluation, outcome file, or QP-labeling artifact was consulted.

## CLI discovery and corpus calls

1. `uv run fedcourts paths --court scotus --docket 9026000245 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was on a read-only filesystem. No corpus lookup completed. Reissued with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache`; it resolved the case and event paths and labeled the outcome evaluator-only. Repeated successfully later to confirm paths. No outcome was opened.
2. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --help` returned the structured-filter CLI help.
3. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` returned U.S. DOGE Service, No. 25-1103; Corey Duran Berry, No. 25-7026; and Blanche v. Ozurumba, No. 25-1343, all recorded as granted on October 13, 2026, with distribution counts two, five, and two. These are not substantive ATA comparators. The first rendering truncated the combined command output, so its transfer line was not retained in the visible return; it is not estimated here. The command was repeated with stdout projected through `jq` to retain a compact result and the exact stderr transfer line:

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

   This was a warm-cache repeat, not a claim about the initial request's transfer. `--decided-before 2026` masks by derived Term/year rather than imposing a January 1, 2026 calendar boundary; the returned prior-Term petitions therefore include calendar-2026 grants. This is a forward cell and all returned grant dates precede the prediction date.
4. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --court scotus --citation '598 U.S. 471' --decided-before 2026 --limit 2` returned no rows and warned that only 200 scoped SCOTUS rows carry any reporter citation. This is missing citation coverage, not absence of the precedent.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## Web attempts

5. Web search: `site.supremecourt.gov opinions Twitter Taamneh 598 471 2023 aiding abetting conscious voluntary culpable participation`. The tool returned no usable content. No evidence was taken from it.
6. Web open of the official Supreme Court Taamneh slip-opinion PDF, identified by the path `/opinions/22pdf/21-1496_d18f.pdf`. The tool again returned no usable content. No evidence was taken from it. Neither web call sought the present petition's disposition.

## CourtListener MCP calls

7. Opinion search with citation `144 F.4th 420`, requesting two results and the case-name/date/citation/opinion fields. Query `9e9bb960` returned count zero. Ashley's competing interpretations remain grounded in the provisioned party briefs, not an independent opinion read.
8. Opinion search with citation `598 U.S. 471`, requesting two results. Query `2945ae1f` returned four matching records, displaying two versions of Twitter, Inc. v. Taamneh, dated May 18, 2023. Opinion IDs included 10516287 and 9395548. No additional page was requested.
9. Within-opinion literal search on opinion 9395548 for `unusual`, with 900 characters of surrounding context. Returned one excerpt discussing the possibility that routine services supplied unusually to known terrorists can support aiding-and-abetting liability, following the rejection of the particular social-media allegations. This qualification informed the assessment of respondents' vehicle and factual-distinction arguments. No current-petition opinion or docket was queried.
