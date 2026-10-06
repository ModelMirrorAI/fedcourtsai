# Retrieval log

## Local inputs and base rates

- Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction/tooling/flags schemas, and the provisioned event, context, snapshot, and filed-document material. Reviewed the petition and BIO's substantive cert arguments; no other predictor output or outcome artifact was consulted.
- Ran `uv run fedcourts paths --court scotus --docket 73500259 --event evt-order-cvsg-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This is path resolution, not corpus retrieval.
- Read the committed `metrics/statpack.md`: modern cert, originating-circuit, paid-segment relist and CVSG cuts, and the sal-v4 reached-band table. Used only displayed 2017–2024 high-band reached rows for the numerical anchor. A local Python calculation weighted their rounded rates by n, producing 0.3495100223 over n=898. No `fedcourts query`, `open-events`, or `stats` call was made; there is no ranged-corpus transfer line to report.

## Web searches

Both `web.run` requests returned no usable content or source references. Neither supplied facts to the forecast:

1. `site.supremecourt.gov opinions 2003 Empagran 03-724 foreign injury independent domestic effect`
2. `F Hoffmann La Roche Empagran 542 U.S. 155 2004 independent foreign injury Supreme Court opinion`

These were general historical-authority searches, not searches for this cell's case or outcome.

## CourtListener MCP

1. `search(type="o", citation="542 U.S. 155", num_results=1)`: returned an unrelated Gaito result, not used. The citation filter was insufficiently discriminating.
2. `search(type="o", court="scotus", case_name="Empagran", filed_before="2005-01-01", num_results=2, fields=["caseName","dateFiled","opinions","absolute_url","citation"])`: located the June 14, 2004 Empagran opinion, opinion ID 136989. An additional historical procedural order appeared but was not used.
3. `search_document(opinion_id=136989, query="independent", snippet_size=450)`: read excerpts confirming the independent-foreign-harm limitation. Citation: F. Hoffmann-La Roche Ltd. v. Empagran S.A., 542 U.S. 155, 158–60 (2004).
4. `search(type="o", court="ca7", case_name="Motorola Mobility", filed_after="2014-11-01", filed_before="2015-02-01", num_results=3, fields=["caseName","dateFiled","opinions","citation"])`: located the original Motorola opinion, ID 2755741, and the January 12, 2015 amended opinion, ID 2769070. An unrelated printing-contract decision also appeared and was not used.
5. `search_document(opinion_id=2769070, query="determined", snippet_size=1000)`: read amended-opinion excerpts about U.S.-determined purchase prices, corporate separateness, and domestic injury, PDF pp. 12–14.

No live CourtListener docket for NHK/Seagate, current case search, subsequent history, or disposition was retrieved. Historical authorities were used as doctrinal context, not as a sampled empirical prior.
