# Retrieval record

## Local inputs and contract

Read .github/prompts/predict.md and schemas/prediction.schema.json before case facts; also consulted schemas/agent_tooling.schema.json and schemas/agent_flags.schema.json for output shapes. Read this event's event.yaml and the case-level record/snapshots/2026-09-30.json, record/context.json, record/same-question.json, and record/documents/{documents.json,questions-presented.txt,petition.txt,appendix.txt}. Substantive document review centered on the petition's question, facts, vehicle and summary-reversal arguments, and the appendix's complete opening state-court decisions. Read metrics/statpack.md's modern-cert, prior-Term sal-v7 reached-band, relist, CVSG, and amicus tables. Did not read outcomes, other predictions, evaluations, or qp-topics artifacts.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000218 --event evt-order-call-for-response-disposition --role predictor` failed because the default uv cache was read-only. No case data returned and no install was attempted.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000218 --event evt-order-call-for-response-disposition --role predictor` succeeded and confirmed case/event paths; the outcome was described only as evaluator-only.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` returned structured-filter usage. DECIDED_BEFORE was not set; I nevertheless supplied a prior docket-Term bound to the two queries below.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '577 U.S. 385' --decided-before 2026 --limit 3` returned no matching prior and warned that only 200 in-scope SCOTUS rows carry reporter citations. This was treated as a coverage gap, not as evidence Wearry does not exist.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --decided-before 2026 --limit 3` returned U.S. DOGE Service v. United States District Court (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343). All were unrelated grants, dated October 13, 2026. The filter's docket-Term clock does not guarantee pre-snapshot decision dates. This is a forward cell, but these results were not used as contemporaneous analogies or to adjust the forecast. None concerned this cell's own disposition.

   `ranged corpus reads: 29 GET(s), 7602176 byte(s)`

## Web attempts

1. Search query: `site.supremecourt.gov opinions 2015 Wearry Cain 14-10008 materiality`. No usable output returned.
2. Search query: `Wearry v Cain 577 U.S. 385 opinion Supreme Court March 2016`. No usable output returned.
3. Open attempted: `https://www.govinfo.gov/content/pkg/USREPORTS-577/pdf/USREPORTS-577-385.pdf`. No usable output returned. No facts were inferred from these empty responses.

## CourtListener MCP

1. `search(type="o", citation="577 U.S. 385", num_results=1)` identified Wearry v. Cain, filed March 7, 2016, cluster 3183098 and combined opinion 3183080. It also supplied the original Supreme Court opinion's download location. No own-case search was made.
2. `read_document(opinion_id=3183080)` returned the combined majority/dissent text, 74,722 characters with display truncation. Used the majority's explanation that it reverses denial of Louisiana state postconviction relief for withheld material evidence, and its discussion of attacks on the core witnesses. This is independent historical precedent, not Matthews's judgment.
3. `search_document(opinion_id=3183080, query="cumulative", snippet_size=650)` returned two contextual matches confirming the majority's criticism of evidence-by-evidence evaluation instead of cumulative materiality review.

No live docket, own-case decision, later own-case document, or outcome coverage was retrieved. No packages were installed. The required cell validation is a local output check, not substantive retrieval.
