# Retrieval record

No lookup sought Nguyen's own Supreme Court disposition, subsequent history, current docket, or later filings. The case-specific evidence came from the provisioned September 9 snapshot, context, questions presented, petition, manifest, and selected appendix passages. No other cell's output or QP-topic artifact was read.

## Local reference material and CLI

- Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction and tooling schemas, and the relevant sections of committed `metrics/statpack.md` and `metrics/statpack.json`. Calculated the 2017–2025 sal-v4 baseline reached pool directly from JSON: 660 / 12,913 = 5.11112832%. No live corpus census or current corpus vintage was obtained.
- `uv run fedcourts paths --court scotus --docket 9026000019 --event evt-order-call-for-response-disposition --role predictor` failed before execution because the default uv cache was read-only. Reran successfully with `UV_CACHE_DIR=/tmp/uv-cache`; it resolved the case and event paths and explicitly withheld the outcome path. No outcome was read.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` displayed the supported structured filters.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '489 U.S. 538' --decided-before 2026-09-10 --limit 1` returned no prior. Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. It applied the supplied September 10 boundary and warned that only 200 SCOTUS rows in scope had reporter citations, so an empty citation result was likely a coverage limitation. The cell remains forward; the voluntarily restrictive query boundary did not change its mode. No repeated sparse-filter lookup was attempted.
- Read the path and serialization helpers and the relevant prediction-model validation code to check the output contract. These were implementation references, not additional case evidence.

## Web search attempts

1. First `web.run` batch searched `Blanton North Las Vegas 489 U.S. 538 additional statutory penalties six months jury`; `site.nv.findacase.com Anderson 2019 domestic battery jury firearms Supreme Nevada`; and `site.nvbar.org Anderson Eighth Judicial 2019 135 Nev jury domestic battery`. The tool returned no visible result content. No facts were taken from it.
2. Second `web.run` batch searched `Blanton North Las Vegas 489 U.S. 538` and `Anderson Eighth Judicial District Court 448 P.3d 1120 2019 jury trial`. Again no visible result content was returned. The reporter string in that exploratory query was not verified and is not relied upon or cited as authority.

## CourtListener MCP

1. `search(type="o", q='caseName:(Anderson) AND "domestic" AND "jury"', court="nev", filed_before="2026-09-10", num_results=3)` returned one irrelevant 1913 case, Anderson v. Berrum. Disregarded.
2. `search(type="o", q='"Anderson" "2019"', citation="448 P.3d 1120", num_results=3)` returned zero results. The attempted citation was not confirmed.
3. `search(type="o", q='"Andersen" "jury"', court="nev", filed_after="2019-01-01", filed_before="2020-01-01", num_results=3)` returned Andersen (Christopher) v. District Court (City of Las Vegas), September 12, 2019, neutral citation 2019 NV 42, cluster 5304871, opinion 5133431. The spelling correction identified the primary authority cited in the petition.
4. `read_document(opinion_id=5133431)` returned the Andersen opinion (23,794 characters reported; the displayed response was abbreviated). Used its holding that Nevada's added state firearm prohibition makes misdemeanor domestic battery serious enough for a jury, and its distinction from federal-only collateral restrictions.
5. `search_document(opinion_id=[5133431], query="federal", snippet_size=1000)` returned two passages. These confirmed the coextensive federal/state jury-right framework and the distinction between the state firearm amendment and the earlier federal-only restriction.
6. `get_endpoint_item(endpoint_id="clusters", item_id=112215, fields=["case_name", "sub_opinions", "date_filed", "citations"])` verified Blanton v. City of North Las Vegas, March 6, 1989, 489 U.S. 538, and opinion ID 112215.
7. `read_document(opinion_id=112215, chunk_index=0, chunk_size=17000)` returned the first chunk of Blanton. Used its six-month presumption, the additional-statutory-penalties exception, and the decision's application to the DUI penalties. No Nguyen material appeared in these lookups.

All substantive external authorities used are primary judicial opinions issued before the provisioned case boundary. Administrative schema/data validation is performed separately from evidentiary retrieval.
