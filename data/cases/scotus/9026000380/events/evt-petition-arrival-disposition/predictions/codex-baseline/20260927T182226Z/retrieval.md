# Retrieval log

## Local context beyond the provisioned case inputs

- Read `metrics/statpack.md`, focusing on modern discretionary-cert dispositions, paid-segment relist/CVSG cuts, and the sal-v4 per-Term salience-band table.
- Read `metrics/statpack.json` for exact prior-Term federal reached denominators and rates. Used `jq` to filter Terms 2017–2025 and sum `prefix_weighted_resolved * prefix_est_grant_rate` over `prefix_weighted_resolved`: 143 / 202 = 0.7079207920792079. No live corpus query, opinion hydration, or ranged corpus read occurred.
- Read task instructions and the prediction, flags, and tooling schemas for the output contract. Ran `uv run fedcourts paths --court scotus --docket 9026000380 --event evt-petition-arrival-disposition --role predictor`; the first attempt failed because the default uv cache was read-only. The retry with a temporary writable cache succeeded. No outcome file was opened.

## Web attempts

The following general-context searches returned no usable results or source text:

1. `site.supremecourt.gov Rule 10 certiorari conflict courts appeals`
2. `site.supremecourt.gov opinions Jennings Rodriguez 1252(b)(9) 2018 detention`
3. `Supreme Court Rule 10 considerations governing review certiorari`
4. `Jennings v Rodriguez 583 U.S. 281 2018 1252 b 9`
5. Open request for `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

No substantive inference rests on these empty tool returns. None was a search for this case or its disposition.

## CourtListener MCP

1. `search(type="o", citation="583 U.S. 281", num_results=3, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Returned Jennings v. Rodriguez, decided February 27, 2018, opinion ID 4248498, and an unrelated search hit (John A. Nelson Co. v. Helvering) that was not used.
2. `search_document(opinion_id=4248498, query="We do not interpret", snippet_size=1800)`. No matches.
3. `search_document(opinion_id=4248498, query="comprehensive", snippet_size=1400)`. Read the passage declining a comprehensive interpretation of § 1252(b)(9), explaining the particular claims not barred there, and discussing the narrow treatment of § 1252(g). Used only as general preexisting legal context; it provides no information about this petition's outcome.

No current-case outcome, later docket history, prohibited topic-label artifact, or other predictor's output was consulted.
