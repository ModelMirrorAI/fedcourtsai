# Retrieval log

## Local context beyond the provisioned case inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas for the output contract.
- Read `metrics/statpack.md`: modern-cert disposition population, originating-court context, paid-segment relist/CVSG cuts, and sal-v4 prior-Term reached-band table. A broad initial read also displayed era, interim, and merits sections, which were not used as cert anchors. Used a local Python calculation to pool only the displayed 2017–2025 baseline reached rates by their denominators: 12,720 weighted resolved petitions and approximately 5.0109% grants.
- Ran `uv run fedcourts paths --court scotus --docket 9026000095 --event evt-petition-disposition --role predictor`. The initial attempt failed because the default uv cache was read-only; rerunning with a writable temporary cache succeeded. No outcome file was opened.
- No `fedcourts query` or `open-events` calls; no ranged corpus reads or transfer lines.

## Web attempts

1. `web.run` search: `site.supremecourt.gov Rule 10 considerations governing review certiorari`.
2. In the same call, search: `site.supremecourt.gov opinions Caperton Massey 556 868 probability bias extreme facts`.
3. `web.run` open of the Cornell Supreme Court Rule 10 page (`https://www.law.cornell.edu/rules/supct/rule_10`).

Both tool calls returned empty visible responses, without usable content or source identifiers. No proposition depends on a successful web retrieval.

## CourtListener MCP

1. `search(type="o", citation="556 U.S. 868", num_results=1)`: returned the historical Caperton case, decided June 8, 2009; query ID `0f1da902`, cluster/opinion ID `145867`. Search metadata contained combined and separate opinion snippets. This was a precedent-only search, not a search for the forecast case.
2. `search_document(opinion_id=145867, query="exceptional", snippet_size=450)`: returned two excerpts, one from the majority describing the campaign-influence facts as exceptional and one from the dissent criticizing the majority's limiting language. Used only the majority excerpt for the narrow doctrinal comparison in the rationale; did not treat the dissent as the holding.

No current-case outcome, subsequent-history search, or additional case-specific retrieval was performed.
