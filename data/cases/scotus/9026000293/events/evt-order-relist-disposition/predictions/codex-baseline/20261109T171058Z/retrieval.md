# Retrieval record

## Provisioned inputs and committed reference material

Read the target snapshot dated 2026-11-09, context, event definition, petition and questions presented, document manifest, same-question list, and the two provisioned Vide snapshots with their manifest. Consulted the prediction contract and schemas and `metrics/statpack.md` / `metrics/statpack.json`. Read no other predictions, evaluations, outcome file, or `data/qp-topics/` material.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000293 --event evt-order-relist-disposition --role predictor` failed before execution because uv's default cache was read-only. No data were retrieved. A chained `query --help` therefore did not execute.
2. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts paths --court scotus --docket 9026000293 --event evt-order-relist-disposition --role predictor` succeeded and resolved the target event. The evaluator-only outcome was not opened.
3. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --help` succeeded; a second invocation piped to `sed -n '60,125p'` inspected the disposition, era, and clock options. These were help calls, not corpus retrievals.
4. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 4` returned Heidi Cid v. United States (26-5123; November 9, 2026), Burford German Funding v. financialright claims (25-1269; October 19, 2026), Roofing Designs by JR v. Royal American Construction (25-1367; October 13, 2026), and Pedro Jose Silva Ochoa v. United States (25-7569; October 13, 2026). These are other cases, not the target or its companions. The combined terminal output was truncated, and the transfer line from this first invocation was not visible in the retained display; I do not estimate it. No opinion bodies were fetched.
5. Repeated the same query, piping its JSON rows to `jq -c '{case_name,docket_number,date_cert_granted,disposition,distribution_count,has_opinion}'` to obtain an untruncated result summary and transfer line. It returned the same four cases. Cid had one distribution, the other three two; all had `has_opinion: false`.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

   The zero is the repeated lookup's warm-cache report, not a representation that the first lookup transferred nothing. The query is selected on GVR disposition and supports only procedural examples, not an estimated grant rate.

## Web calls

1. One `web.run` search call used two queries: `site.supremecourt.gov opinions Exxon Mobil Corporacion CIMEX 24-699` and `site.ca2.uscourts.gov Havlish Taliban 23-444 August 26 2025 sovereign immunity`. The objective was the intervening precedent and the lower-court decision, not the target petition's disposition. Results included the official Supreme Court opinion and lower-court reports, along with secondary commentary. Secondary reports were not relied on for the forecast; the provisioned appendix supplied the lower-court reasoning. No target-petition disposition surfaced.
2. Opened the official Supreme Court opinion PDF, `https://www.supremecourt.gov/opinions/25pdf/24-699_f204.pdf`, *Exxon Mobil Corp. v. Corporación CIMEX, S.A. (Cuba)*, No. 24-699, decided June 18, 2026. Read the syllabus and relevant jurisdictional-immunity analysis. This is the intervening precedent, not the case being predicted.
3. Searched that same PDF for `execution` with `web.run find`; the result highlighted opinion p. 5 n.2, distinguishing execution immunity from the jurisdictional question presented. Used this only to assess how directly the precedent supports the requested GVR.

No CourtListener MCP call, live target docket lookup, package installation, or further external retrieval was attempted. Cell validation is local output verification, not legal retrieval.
