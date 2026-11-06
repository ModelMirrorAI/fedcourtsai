# Retrieval record

## Local inputs and reference material

Read the prediction contract and schema, the named event, the November 6 snapshot, documents metadata, questions presented, petition and relevant bound appendix passages, context.json, and same-question.json. Consulted the committed metrics/statpack.md and metrics/statpack.json, including the strictly prior-Term sal-v7 state-band reached pool (98/420). No other prediction, evaluation, or outcome artifact was read.

Administrative commands: the first `uv run fedcourts paths --court scotus --docket 9026000037 --event evt-petition-disposition --role predictor` failed on the read-only default uv cache. The same command succeeded with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`. Query help was consulted twice, once with `COLUMNS=110` for narrower output. These invocations installed nothing. The required cell validation is a local output check, not retrieval of case evidence.

## Corpus calls

Each command below used `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`. No replay clock was exported; the voluntary 2026 Term bar on the first two calls excludes this petition's docket Term without asserting a decision-date cutoff.

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 4`
   Returned U.S. DOGE Service (25-1103), Corey Duran Berry (25-7026), Todd Blanche v. Ozurumba (25-1343), and Missionaries of Saint John the Baptist (25-1131). Their distribution counts were 2, 5, 2, and 2, respectively; none showed a CVSG. No opinion bodies were requested. The initial transfer line was not retained in the tool's truncated rendered output; its transfer volume is unknown here, not assumed to be zero.
2. Repeated the identical query, piping stdout through jq to retain only identifying and distribution fields and keep the transfer report visible. Same four results.
   `ranged corpus reads: 0 GET(s), 0 byte(s)`
3. `uv run fedcourts query --court scotus --era 1990s --citation '509 U.S. 688' --limit 1`
   No row returned. The tool warned that only 200 scoped SCOTUS rows carry reporter citations and that an empty citation lookup usually reflects sparse coverage. No retry of this sparse filter.
   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## CourtListener MCP calls

1. `search(type="o", citation="459 U.S. 359", court="scotus", num_results=1)`: Missouri v. Hunter, January 19, 1983; cluster 110824, lead opinion 9428993. A second matching result was not opened.
2. `search_document(opinion_id=9428993, query="bound", snippet_size=1300)`: checked the distinction at pages 368–69 between binding state statutory construction and reviewable federal constitutional conclusions; two snippets, no full opinion retrieval.
3. `search(type="o", citation="115 F.3d 1431", num_results=1, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`: United States v. Nash, June 25, 1997; opinion 741894.
4. `search_document(opinion_id=741894, query="rather than", snippet_size=900)`: four snippets, including the statutory-elements rather than indictment passage at 1437–38; unrelated snippets supplied no forecast input.
5. `search(type="o", citation="439 F.3d 796", num_results=1, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`: United States v. Gamboa, March 3, 2006; opinion 793501.
6. `search_document(opinion_id=793501, query="specific charges", snippet_size=1200)`: one snippet supporting the indictment-specific approach at page 809. No subsequent-history search was made.

## Web searches

Two web.run search calls were attempted. Neither returned readable result content, so neither informed a factual or legal conclusion.

First call, three queries:
- `site.supremecourt.gov about biographical sketches current members Court`
- `site.loc.gov "Missouri v. Hunter" "bound" "368"`
- `site.loc.gov "Michigan v. Long" "plain statement"`

Second call, two queries:
- `Missouri v Hunter 459 U.S. 359 368 bound state statutes`
- `Michigan v Long 463 U.S. 1032 plain statement federal law`

No search or docket lookup sought this petition's own outcome. The Justice labels follow the provisioned prediction contract's roster. There was no retrieved outcome to disclose.
