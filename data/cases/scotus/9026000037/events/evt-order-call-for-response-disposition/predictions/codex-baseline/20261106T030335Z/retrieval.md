# Retrieval log

## Local contract, record, and reference material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the cell's `event.yaml`, and the case-level provisioned snapshot, context, document manifest, questions presented, petition with bound-in appendix, and same-question file. Consulted the committed `metrics/statpack.md`, the tooling/flags schemas, and the claims/Justice-roster implementation to check output conventions. No other prediction, evaluation, realized outcome, or `data/qp-topics/` material was read.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000037 --event evt-order-call-for-response-disposition --role predictor` failed before execution: uv could not write its default cache under the read-only home directory. No case data returned.
2. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --offline fedcourts paths --court scotus --docket 9026000037 --event evt-order-call-for-response-disposition --role predictor` succeeded and confirmed the cell paths; the evaluator-only outcome path was not disclosed or opened.
3. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --offline fedcourts query --help` was run three times, once in full and twice with shell output selection (`tail -65`, then `sed -n '65,140p'`), to read the structured filters and limit/clock options. These were help calls, not corpus retrievals.
4. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --offline fedcourts query --court scotus --citation '459 U.S. 359' --decided-before 2026 --limit 2` returned no rows. Its warning states that only 200 in-scope rows carry citations and that empty results do not establish absence of the case.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

5. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --offline fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` returned U.S. DOGE Service v. United States District Court for the District of Columbia (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche, Attorney General v. Izuchukwu Ozurumba (25-1343), all with October 13, 2026 grant stamps. The clock is a docket-Term filter, not a calendar-date bar; these are different cases in a forward cell, not this petition's outcome. No opinion bodies were requested. They were not used as substantive analogues or a calibrated comparison sample.

   `ranged corpus reads: 30 GET(s), 7864320 byte(s)`

## Web searches

One `web.run` call submitted two searches: `site.loc.gov "Missouri v. Hunter" "459" "359"` and `site.loc.gov "Michigan v. Long" "plain statement"`. The tool returned no usable source text. Neither search concerned this petition's outcome; neither supplied a fact used in the forecast.

## CourtListener MCP

1. `search(type="o", citation="459 U.S. 359", court="scotus", num_results=1)` identified Missouri v. Hunter, decided January 19, 1983, including combined opinion 110824.
2. `search_document(opinion_id=110824, query="bound", snippet_size=600)` returned the distinction between accepting a state court's statutory construction and reviewing its federal double-jeopardy conclusion. This verified and qualified the petition's reliance on Hunter.
3. `search(type="o", citation="115 F.3d 1431", num_results=1)` identified United States v. Nash, June 25, 1997, opinion 741894.
4. `search_document(opinion_id=741894, query="rather than the way", snippet_size=450)` verified that the Ninth Circuit looked to offense elements rather than the way offenses were charged.
5. `search(type="o", citation="439 F.3d 796", num_results=1, fields=["caseName","citation","opinions","absolute_url","dateFiled"])` identified United States v. Gamboa, March 3, 2006, opinion 793501.
6. `search_document(opinion_id=793501, query="specific charges", snippet_size=500)` verified that the Eighth Circuit considered specific indictment charges as well as statutory provisions.

No live CourtListener query or web lookup targeted New Mexico v. Neal, its subsequent history, or its disposition. No external lower-court opinion for this case was needed because the provisioned petition contains the state high court's decision.
