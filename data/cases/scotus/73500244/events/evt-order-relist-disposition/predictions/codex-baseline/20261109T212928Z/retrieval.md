# Retrieval record

## Local reference materials

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, and the relevant cert sections of `metrics/statpack.md`. Read the event definition and case-level provisioned snapshot, context, document manifest, question presented, petition, opposition, reply, appendix, decision below, and lower-court docket summary. No other prediction, evaluation, realized outcome, or topic-labeling artifact was read.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 73500244 --event evt-order-relist-disposition --role predictor` failed before execution because `/home/codexcell/.cache/uv` was read-only.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 73500244 --event evt-order-relist-disposition --role predictor` succeeded and identified the case and event paths. The outcome path was explicitly not supplied for this role.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` succeeded; a second display with `COLUMNS=180` and `sed -n '25,67p'` made the structured filter descriptions readable. These were help calls, not corpus lookups, and printed no transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2025 --limit 3` succeeded.

   `ranged corpus reads: 79 GET(s), 20643840 byte(s)`

   Returned RiseandShine v. PepsiCo (24-1016), Monsanto v. Durnell (24-1068), and Hikma v. Amarin (24-889). Each had three distributions, a CVSG, and no opinion text. The bare-year filter operates on docket/best-known year rather than guaranteeing a pre-2025 grant date; these rows reported later grant dates. This is a forward cell, so that is not a timing breach, but I did not treat them as a strictly prior resolved sample. They are not subject-matter analogues, and a grants-only query cannot supply a rate. No `--full` hydration or `open-events` lookup was attempted.

## Web attempts

5. One `web.run` search call contained two searches: `site.ca10.uscourts.gov "Chavarria" "2025" "1268"` and `site.supremecourt.gov "Lopez" "514" "instrumentalities"`. The tool returned no usable displayed result content. No substantive proposition rests on this attempt.
6. One `web.run` open call attempted the official Tenth Circuit PDF for Chavarria, file `010111250704.pdf`. It returned no usable displayed content. No substantive proposition rests on this attempt.

## CourtListener MCP

7. `search(type="o", citation="140 F.4th 1257", num_results=2)` found United States v. Chavarria, Tenth Circuit, June 16, 2025, cluster 10605317, opinion 11071905, docket 23-2102. This was a precedent lookup, not a lookup of Brown's Supreme Court docket or outcome.
8. `search_document(opinion_id=11071905, query="hold only", snippet_size=2000)` returned the limited holding and conclusion, slip opinion pp. 22–23: generic motor-vehicle allegations were insufficient, and the facial constitutional issue was not decided. Used to evaluate the government's no-square-split argument.
9. `search_document(opinion_id=11071905, query="even if all", snippet_size=1800)` returned zero literal matches. No inference drawn from that failed phrase match.
10. `search_document(opinion_id=11071905, query="all cars", snippet_size=2000)` returned the discussion at slip opinion pp. 19–20 distinguishing cars/automobiles from the broader motor-vehicle class. Used with the limited holding to assess the conflict.

No own-case disposition search, live Supreme Court docket lookup, companion-status retrieval, or subsequent-history lookup was attempted. The CLI schema/JSON inspection, patch creation, and cell validation are local contract/completeness operations, not additional factual retrieval.
