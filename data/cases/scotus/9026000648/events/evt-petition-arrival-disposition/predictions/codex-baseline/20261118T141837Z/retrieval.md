Local reference material consulted beyond the provisioned case inputs: .github/prompts/predict.md; schemas/prediction.schema.json; schemas/agent_tooling.schema.json; schemas/agent_flags.schema.json; and the cert disposition, circuit, relist, CVSG, amicus, and sal-v8 per-Term sections of metrics/statpack.md. Only strictly prior Terms informed the baseline; context.json's frozen anchor controlled. Local file-inventory, text-extraction-by-reading, and schema-inspection commands added no external case material.

CLI setup attempts:

- `uv run fedcourts query --help` failed before retrieval: uv could not initialize /home/codexcell/.cache/uv because that filesystem was read-only. No corpus transfer line.
- `uv run fedcourts paths --court scotus --docket 9026000648 --event evt-petition-arrival-disposition --role predictor` failed for the same cache reason. No corpus transfer line.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --help` succeeded and supplied the supported structured filters. No corpus lookup or transfer line.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts paths --court scotus --docket 9026000648 --event evt-petition-arrival-disposition --role predictor` succeeded, resolving the case and event paths. The evaluator-only outcome was not opened. No corpus lookup or transfer line.

Corpus lookup:

- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 4`
  - Stderr: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`.
  - Returned Robinhood Markets v. Sodha (25-944), Goldman Sachs Bank USA v. Brown (25-1408), U.S. DOGE Service v. U.S. District Court (25-1103), and Corey Duran Berry v. United States (25-7026). Their distribution counts were 3, 4, 2, and 5; Robinhood recorded a CVSG. No opinion bodies were requested. The 2026 argument is a docket-Term mask, not a calendar-date restriction; these OT2025 dockets include grants in calendar 2026. The sample is selected on a grant and was not used as a numerical grant-rate estimate. None is this petition.

CourtListener MCP lookups, all concerning the older conflicting Ninth Circuit authority, not this petition's disposition:

1. `search(type="o", citation="89 F.4th 1094", court="ca9", fields=["caseName","dateFiled","citation","cluster_id","absolute_url","opinions"], num_results=3)` returned one match, California Restaurant Association v. City of Berkeley, cluster 9391830, opinion 9387306. Search metadata lists the original 2023 filing date; the provisioned papers cite its 2024 reported version. Source: https://www.courtlistener.com/opinion/9391830/cra-v-city-of-berkeley/ .
2. `search_document(opinion_id=9387306, query="preempts", snippet_size=650)` returned 18 matches. The opinion excerpts confirm that EPCA preempts Berkeley's prohibition on natural-gas piping in new buildings. The broad response also included discussion of the government's narrower position. Displayed output was lengthy; I relied on the directly relevant holding excerpts.
3. `search_document(opinion_id=9387306, query="United States", snippet_size=450)` returned broad government/citation matches. This added no decisive substantive inference; I narrowed the search in the next call.
4. `search_document(opinion_id=9387306, query="The federal government, as amicus", snippet_size=400)` returned one match, confirming that the government had argued for narrower preemption in Berkeley. I distinguished that earlier position from the support for challengers documented in the provisioned Second Circuit opinion and petition.

No web searches, live Supreme Court docket requests, other predictions, or requests for this petition's outcome were made. CourtListener tools were discovered through the available tool registry; no REST fallback was used. The cell-validation command is a local output check and retrieves no additional evidence.
