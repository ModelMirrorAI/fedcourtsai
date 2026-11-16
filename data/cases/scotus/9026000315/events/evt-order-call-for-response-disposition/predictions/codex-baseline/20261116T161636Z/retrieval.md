# Retrieval record

## Provisioned inputs

Read the event definition, November 5, 2026 snapshot, questions presented, petition and relevant appendix passages, document manifest, context, and same-question file under `data/cases/scotus/9026000315/record/`. The event definition is under its event directory. These established the frozen information set. No other prediction, evaluation, realized outcome, or `data/qp-topics/` material was read.

## Local reference material and CLI

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json` for the output contract. Inspected the prediction schema's relevant definitions programmatically.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions and circuit cuts; paid-segment relist, CVSG and amicus cuts; salience overview; and the sal-v8 prior-Term reached-rate table. The frozen anchor and amicus reference in context, rather than an own-Term outcome population, supplied the numerical starting points.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000315 --event evt-order-call-for-response-disposition --role predictor`. Failed before execution because the default uv cache path was read-only.
- Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run --offline fedcourts paths --court scotus --docket 9026000315 --event evt-order-call-for-response-disposition --role predictor`. Succeeded and returned case, corpus and event paths; the outcome path was expressly withheld. No corpus query or ranged corpus read was performed, and no `ranged corpus reads:` line was produced.

## Attempted web retrieval

1. One `web.run` search call with the queries `Mosser v Darrow 341 U.S. 267 1951 trustee negligence supreme justia` and `In re Mailman Steam Carpet Cleaning 196 F.3d 1 1999 trustee personally liable negligence opinion`. The tool returned no readable payload or usable source; no factual inference rests on it.
2. One `web.run` open request for `https://www.ca1.uscourts.gov/sites/ca1/files/opnfiles/99-1865-01A.pdf`. This was an attempted historical-opinion retrieval, not this petition's docket. It likewise returned no readable payload; the guessed path was not verified and is not a source for the prediction.

## CourtListener MCP

1. `search(type="o", citation="196 F.3d 1", num_results=3)`, query ID `4eb89844`. Returned two irrelevant citation-token matches and the matching First Circuit case, *LeBlanc v. Salem / In re Mailman Steam Carpet Cleaning Corp.*, decided November 2, 1999, opinion 198701. Only the matching case informed the analysis.
2. `search_document(opinion_id=198701, query="split", snippet_size=2200)`. Returned one passage identifying the division over trustees' personal liability for negligence and the opposing circuit authorities. Used to corroborate that the petition identifies a longstanding real disagreement.
3. `search(type="o", court="ca5", q='"725 F.3d 498"', num_results=1, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`, query ID `91c51fde`. Returned *Liberty Mutual Insurance v. United States ex rel. Lamesa National Bank (In re Schooler)*, decided August 7, 2013, opinion 1036824. The search reported two matches but returned the requested one; no pagination was requested.
4. `search_document(opinion_id=1036824, query="gross negligence", snippet_size=850)`. Returned 14 excerpts, including the surety-bond posture, the Fifth Circuit's gross-negligence rule, and discussion of the federal trustee program's historical contrary position. The displayed response was partly truncated; I did not treat unshown text as read.
5. `search_document(opinion_id=1036824, query="some courts", snippet_size=2100)`. Returned one focused passage from footnote 10 acknowledging negligence and willful-and-deliberate approaches, explaining the Fifth Circuit's intermediate standard, and describing the government's historical objection. Used to verify the three-way split and the possibility of a federal institutional interest, not to assume any recommendation in this case.

The external case texts were primary judicial opinions. No query sought this petition's disposition, later history, or someone else's forecast. No current Supreme Court docket retrieval was attempted. Validation of the completed output directory is a local contract check, not substantive retrieval.
