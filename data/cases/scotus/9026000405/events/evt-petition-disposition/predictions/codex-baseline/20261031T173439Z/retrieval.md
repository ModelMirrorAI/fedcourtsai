# Retrieval record

## Local context beyond the provisioned record

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json` for the contract.
- Read `metrics/statpack.md`: modern-cert dispositions and circuit cuts, paid-segment relist/CVSG/amicus cuts, salience bands, and prior-Term reached-band table. Used the provisioned frozen cert anchor as the primary reference.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000405 --event evt-petition-disposition --role predictor`. It failed to initialize the default read-only uv cache. Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000405 --event evt-petition-disposition --role predictor`; it returned the case, corpus, and event paths without an outcome path. Neither call was a corpus query and neither printed a ranged-corpus-reads line.
- Used local file listing, text reads/searches, schema inspection with `jq`, and `git status --short`. Did not inspect another prediction, an evaluation, or an outcome artifact.

## External precedent retrieval

1. Web search with queries `Moe United States 326 F.3d 1065 FECA emotional distress scope` and `Fuqua United States Postal Service 956 F.3d 961 FECA 2020`. The tool returned no visible results; no source from it informed the legal analysis.
2. CourtListener MCP `search(type="o", citation="326 F.3d 1065", num_results=2)`: one result, *Marilyn Moe v. United States*, Ninth Circuit, April 18, 2003; opinion 781702.
3. CourtListener MCP `read_document(opinion_id=781702, chunk_index=0, chunk_size=16000)`: retrieved the scope/entitlement distinction and the holding that psychological injury accompanied by physical injury fell within FECA. Read the returned first chunk, not the unreturned remainder.
4. Web search with query `"Fuqua" "956 F.3d 961"`: again no visible results and no usable source.
5. CourtListener MCP `search(type="o", citation="956 F.3d 961", num_results=1)`: one result, *Leonard Fuqua v. USPS*, Seventh Circuit, April 23, 2020; opinion 4528250, cluster 4747903.
6. CourtListener MCP `search_document(opinion_id=4528250, query="substantial", snippet_size=1800)`: six matches reported; returned excerpts set out the substantial-question referral rule and the distinction between lack of proof and lack of coverage.

No `fedcourts query` or `open-events` calls were attempted. No search sought this petition's disposition, later history, or decision coverage. No external result revealed its outcome.

## Validation

Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data`: `OK: 29762 artifact(s) valid, 71083 reference(s) consistent`. This checks artifacts rather than retrieving legal evidence.
