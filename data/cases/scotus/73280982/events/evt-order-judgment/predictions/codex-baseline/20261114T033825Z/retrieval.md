# Retrieval record

## Local contract and provisioned material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; resolved the cell with `fedcourts paths`; inspected the event and case-level snapshot, context, manifest, questions presented, lower-court docket summary, and relevant portions of all provisioned advocacy and the decision below. Read the committed merits and per-Justice sections of `metrics/statpack.md` and corresponding `metrics/statpack.json` data, with a keyword check of `metrics/README.md`. No outcome file, other prediction, evaluation, or topic-labeling artifact was read.

The initial `uv run fedcourts paths --court scotus --docket 73280982 --event evt-order-judgment --role predictor` failed because the default uv cache directory was read-only. Repeating it with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. Subsequent uv commands use that setting. The command correctly resolved the event and identified outcome material as evaluator-only without opening it.

## Corpus attempts

1. `uv run fedcourts query --help` — read the structured filter interface; no transfer line.
2. `uv run fedcourts query --court scotus --citation '601 U.S. 257' --limit 1` — no matching row; CLI warned that only 195 scoped rows carry citations, so absence is not evidence against the precedent. Switched to MCP for this opinion rather than retrying sparse citation filters.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
3. `uv run fedcourts query --court scotus --disposition granted --era roberts --limit 3` — rejected: era accepts decade tokens, not Chief Justice names. The error printed the supported vocabulary. No transfer line.
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 3` — succeeded. Returned recent cert grants, including this case's already-provisioned November 13 grant and no merits judgment for it. These are cert dispositions, not resolved merits analogues; they supplied no substantive adjustment. No previously unknown outcome of the target merits event appeared.
   - `ranged corpus reads: 24 GET(s), 6225920 byte(s)`
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2025 --limit 3` — returned RiseandShine v. PepsiCo, Monsanto v. Durnell, and Hikma v. Amarin, each with no merits judgment. This coarse Term filter did not yield substantive securities analogues; none was used as an outcome prior. Output was reduced to case identifiers, captions, docket numbers, cert dispositions, grant dates, and merits-judgment fields with jq.
   - `ranged corpus reads: 53 GET(s), 13893632 byte(s)`

## CourtListener MCP

1. `search(type="o", citation="601 U.S. 257", num_results=1)` — located Macquarie Infrastructure Corp. v. Moab Partners, L.P., April 12, 2024; opinion ID 11066691, cluster 10600103. The search returned the official Supreme Court preliminary-print address.
2. `read_document(opinion_id=11066691, chunk_index=1, chunk_size=13000)` — read the Rule 10b-5(b) holding, textual distinction between pure omissions and half-truths, and discussion of Section 11's additional required-statements clause. This is a prior case, not the target litigation.
3. `search(type="o", citation="575 U.S. 175", num_results=1)` — located Omnicare, March 24, 2015, opinion ID 2788684, and its Kagan authorship.
4. `search_document(opinion_id=11066691, query="unanimous", snippet_size=220)` — confirmed Macquarie was a unanimous Sotomayor opinion vacating and remanding.
5. `search_document(opinion_id=2788684, query="not a general disclosure", snippet_size=1100)` — read the discussion explaining that the misleading-omissions clause requires an omitted material fact to render a published statement misleading, rather than merely withholding information.

## Web attempts

1. One `web.run` call submitted two precedent-only queries: `site.supremecourt.gov opinions 2023 Macquarie Moab 22-1165 Sotomayor` and `site.supremecourt.gov opinions 2014 Omnicare Laborers 13-435 Kagan`. No usable result payload was returned.
2. `web.run` attempted to open the official Macquarie preliminary print at `https://www.supremecourt.gov/opinions/23pdf/601us2r13_8mjp.pdf`, the address supplied by MCP. No usable content was returned. Relied on the MCP opinion instead.

No web search named Robinhood or sought its disposition, later history, or anyone's forecast. No target-case outcome or external forecast was encountered.
