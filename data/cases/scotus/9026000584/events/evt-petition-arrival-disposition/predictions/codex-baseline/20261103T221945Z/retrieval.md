# Retrieval beyond the provisioned record

No lookup sought this petition's disposition or subsequent history. All substantive additional retrieval concerned prior opinions or aggregate historical rates.

## Local reference material

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, and `schemas/agent_tooling.schema.json` for the output contract. Located reference files and checked workspace status without reading any other prediction or evaluation.
- Read `metrics/statpack.md`, particularly the paid-segment relist, CVSG, amicus, and sal-v6 reached-band tables. Inspected the corresponding `metrics/statpack.json` term segments with `jq`; pooled OT2017–OT2025 state reached counts to obtain 99/421 = 0.23515439429928742. No OT2026 observations entered the anchor.
- Searched `docs/cli.md` for corpus-query documentation. No case-specific corpus files were opened.

## Corpus CLI calls, including attempts

1. `uv run fedcourts query --help` — failed before querying: default uv cache was read-only. No corpus transfer line.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` — succeeded, displaying structured filters and the provisioned corpus-service interface. No corpus transfer line. `--no-sync` avoided dependency installation.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '576 U.S. 200' --decided-before 2026 --limit 3` — returned no rows. Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. The coverage note said only 200 SCOTUS rows carried reporter citations and an empty result was more likely missing metadata than missing precedent. No claim about Walker's absence was inferred.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000584 --event evt-petition-arrival-disposition --role predictor` — confirmed the supplied case and event paths; explicitly withheld the evaluator-only outcome path. No transfer line. This was path resolution, not an outcome query.

## CourtListener MCP calls

1. `search(type="o", case_name="Mitchell Maryland Motor Vehicle", num_results=3, fields=["id","caseName","dateFiled","citation","absolute_url","opinions"])` — found the Maryland high-court decision of October 28, 2016, 148 A.3d 319, opinion 4093604, and the earlier intermediate appellate decision. The response warned that the requested top-level `id` field was unavailable; nested opinion IDs were supplied.
2. `search(type="o", case_name="Gilliam Gerregano", num_results=2, fields=["caseName","dateFiled","citation","absolute_url","opinions"])` — found the Tennessee Supreme Court decision of February 26, 2025, opinion 10806629, with an official-court PDF reference. This was lower-court precedent retrieval, not a Supreme Court docket lookup.
3. `search_document(opinion_id=[10806629,4093604], query="government speech", snippet_size=350)` — confirmed Gilliam held the characters government speech and Mitchell rejected Vawter's government-speech reasoning. Used summaries rather than copying excerpts.
4. `search_document(opinion_id=2809762, query="do not address", snippet_size=550)` — Walker opinion available, but no literal matches. No inference from that search miss.
5. `search_document(opinion_id=2809762, query="vanity", snippet_size=250)` — found the distinction between specialty and personalized plates near the opening of Walker.
6. `read_document(opinion_id=2809762, chunk_index=0, chunk_size=5000)` — verified that Walker expressly concerned specialty designs rather than the personalization program. Authority: Walker v. Texas Division, Sons of Confederate Veterans, Inc., 576 U.S. 200, 204 (2015).

## Web attempts

1. One `web.run` call with searches `site.supremecourt.gov opinions Walker 2015 vanity plates 14-144` and `site.tncourts.gov Gilliam Gerregano 2025 government speech personalized license plates` — no visible results or source content returned. Neither query concerned this petition's disposition.
2. One `web.run` open of the official Tennessee-court PDF returned by CourtListener, `https://www.tncourts.gov/sites/default/files/OpinionsPDFVersion/Majority%20Opinion%20-%20M2022-00083-SC-R11-CV.pdf` — no visible document content returned. It added no evidence; the usable Gilliam evidence came from MCP.
