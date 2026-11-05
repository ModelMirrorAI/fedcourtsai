# Retrieval record

## Provisioned and local reference material

Read `.github/prompts/predict.md`, the output schemas, the event definition, `record/context.json`, `record/snapshots/2026-11-05.json`, `record/documents/documents.json`, `questions-presented.txt`, the petition, relevant appendix sections including the Nevada opinion, and `record/same-question.json`. Read `metrics/statpack.md`, particularly modern-cert dispositions, the paid-segment relist/CVSG/amicus cuts, and the sal-v7 per-Term risk-set table. No other prediction, evaluation, outcome file, or labeling-measurement artifact was read.

## Corpus and CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000157 --event evt-petition-disposition --role predictor` failed before execution because the default uv cache was read-only. No retrieval occurred.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000157 --event evt-petition-disposition --role predictor` succeeded and identified the event and corpus paths. The outcome was labeled evaluator-only and was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` was called twice: first for the general flags, then with output limited to its initial portion. Both succeeded; neither retrieved priors.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '443 U.S. 595' --limit 2` returned no rows. Its diagnostic explained that only 200 in-scope rows had reporter citations and that absence was likely a coverage issue, not absence of the precedent. No full opinion hydration was requested.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` returned U.S. DOGE Service v. U.S. District Court (25-1103), Berry v. United States (25-7026), and Blanche v. Ozurumba (25-1343). These are unrelated grants, not substantive analogies and not a representative sample for computing a base rate. No opinion bodies were requested. This is a forward cell; the optional year mask was voluntarily used and does not imply a replay cutoff.

   `ranged corpus reads: 29 GET(s), 7602176 byte(s)`

## CourtListener MCP calls

1. `search(type="o", court="ca11", citation="828 F.2d 718", num_results=2, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions"])` returned duplicate records for **Crowder v. Southern Baptist Convention**, decided September 28, 1987, including combined opinion **493995** and separate lead/concurrence records. The records concern the predecessor legal authority, not this petition.
2. `search_document(opinion_id=493995, query="neutral principles", snippet_size=1400)` returned ten contextual matches concerning neutral principles, the church-governance controversy, and the relevant property precedents. Used alongside the petition's specific discussion of Crowder, not as a statistical prior.
3. `search(type="o", court="ca9", citation="844 F.3d 1152", num_results=1, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions"])` returned **Bibiji Kaur Puri v. Sopurkh Kaur Khalsa**, January 6, 2017, opinion **4113720**.
4. `search_document(opinion_id=4113720, query="unaware of any", snippet_size=900)` returned one match expressly allowing purely secular adjudication outside property disputes, subject to ministerial and religious-doctrine limits. This independently confirms the central contrast described in the petition and Nevada opinion.

## Web calls attempted

The following four calls produced no usable content in the returned tool messages. No web snippet, secondary-source characterization, or purported outcome informed this prediction.

1. A two-query search: `site.supremecourt.gov "Hosanna-Tabor" "565"`; `site.ca9.uscourts.gov "Puri" "Khalsa" "2017"`.
2. A two-query search: `Puri v Khalsa 844 F.3d 1152 opinion church neutral principles`; `Hosanna Tabor 565 US 171 Supreme Court opinion pdf`.
3. An attempted open of the government publication page `https://www.govinfo.gov/app/details/USREPORTS-565/USREPORTS-565-171`.
4. An attempted open of `https://cdn.ca9.uscourts.gov/datastore/opinions/2017/01/06/14-36018.pdf`. This guessed docket path was not verified or relied on. The subsequent successful MCP lookup identified a different official download path for Puri; I used MCP opinion text instead and made no additional web request.

No search requested this petition's disposition, subsequent history, or decision coverage. No direct CourtListener REST request was made. Operational schema checks and the required cell validation are local checks, not additional legal retrieval.
