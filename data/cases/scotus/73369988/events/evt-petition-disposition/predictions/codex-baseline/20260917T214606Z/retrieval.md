# Retrieval record

## Local inputs and base rates

Read the prompt, repository instructions, output schemas, this event definition, and this case's provisioned snapshot, context, petition, QPs, and document manifest. Read `metrics/statpack.md` for the modern-cert disposition, originating-court, paid-segment relist/CVSG, and prior-Term sal-v4 reached-band tables. Inspected only the top-level keys of `metrics/statpack.json` for metadata. A local Python calculation pooled the printed 2017–2024 baseline reached rates by printed weighted denominators (approximately 5.12%).

Ran `uv run fedcourts paths --court scotus --docket 73369988 --event evt-petition-disposition --role predictor`; the first attempt failed on the read-only default cache, and the retry with a cache under `/tmp` succeeded. This resolves paths and is not a historical-case lookup. No `fedcourts query` or `open-events` command was used, so no ranged-corpus transfer line was produced. No live corpus freshness was established.

## Web search

One `web.run` call submitted two general queries:

1. `site.supremecourt.gov Rule 10 writ certiorari rarely granted erroneous factual findings misapplication`
2. `site.supreme.justia.com Commonwealth Coatings 393 U.S. 145 White concurrence trivial relationships`

The tool returned no usable result content. Neither query contained this case's name or docket. No evidence from that call entered the forecast.

## CourtListener MCP

1. `search(type="o", citation="393 U.S. 145", num_results=1)`: returned an unrelated Fischer v. Avanade result. Disregarded.
2. `search(type="o", q='caseName:"Commonwealth Coatings"', court="scotus", num_results=2)`: returned historical orders and a paginated result set, query ID `9826eefa`.
3. `search(type="o", q='caseName:"Commonwealth Coatings"', court="scotus", filed_after="1968-11-01", filed_before="1968-12-01", num_results=1, fields=["caseName", "citation", "opinions", "dateFiled"])`: no results.
4. `get_more_results(query_id="9826eefa", num_results=2)`: located the combined Commonwealth Coatings opinion, cluster/opinion 107798, and its separate opinions. Metadata filed date differs from the decision date in the opinion text; used the text's identification of the 1968 decision.
5. `read_document(opinion_id=9423845)`: read Justice White's concurrence, joined by Justice Marshall, concerning disclosure of substantial dealings, trivial relationships, and distinctions between arbitral and judicial standards. This is the only additional opinion text used in the rationale.

No retrieval sought this petition's disposition or subsequent history. No other predictor's work or outcome artifact was consulted.
