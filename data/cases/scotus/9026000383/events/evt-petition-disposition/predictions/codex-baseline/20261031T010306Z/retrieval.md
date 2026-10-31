# Retrieval record

Provisioned inputs: event definition; October 31, 2026 snapshot; context; document manifest; questions presented; petition; appendix; same-question list. Additional local context: `schemas/prediction.schema.json`, agent tooling and flags schemas, `metrics/statpack.md`, and the project metadata. No other prediction or evaluation output was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000383 --event evt-petition-disposition --role predictor` failed before execution because `/home/codexcell/.cache/uv` is read-only. Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000383 --event evt-petition-disposition --role predictor`; returned the expected case and event paths, with outcome explicitly evaluator-only. No outcome was opened.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` succeeded. Called twice; the second display was piped through `head -55` to inspect the option list. No corpus transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era roberts --disposition denied --limit 3` was rejected: eras must be decade tokens. No corpus transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition denied --limit 3` succeeded. Returned three denied substantive interim applications: Louisiana v. Devon Energy Production Company, Jessica Teresa Griffin v. Robert Lee Isaac, and Frank Michael Monte v. United States. They are not comparable cert-petition priors and were not used to estimate the grant probability.

   `ranged corpus reads: 6 GET(s), 1572864 byte(s)`

5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '572 U.S. 650' --limit 1 --full` returned no matching row. Coverage note: only 200 SCOTUS rows carry reporter citations; the empty response does not imply absence of the precedent. No opinion body was returned.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

## Web calls

1. One `web.run` call attempted two general-law searches: `site.supremecourt.gov Rules Rule 10 rarely granted erroneous factual findings misapplication properly stated rule law` and `site.supremecourt.gov Tolan Cotton 572 U.S. 650 2014 summary judgment`. No usable response content was returned.
2. One `web.run` open attempted `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. No usable response content was returned. No claim relies on that attempted rules retrieval.

## CourtListener MCP calls

1. `search(type="o", citation="572 U.S. 650", num_results=1)` verified Tolan v. Cotton, decided May 5, 2014, opinion/cluster 2672535. This is a historical authority cited in the staged petition, not this petition's disposition.
2. `search_document(opinion_id=2672535, query="vacate", snippet_size=900)` returned passages explaining the failure to draw inferences favorably to the nonmovant and the summary vacatur/remand, plus Alito's concurrence discussing Rule 10 and exceptional error correction. Used only to assess the plausibility of a summary-correction route. No further pagination or own-case retrieval.

Validation is a local schema check, not case-outcome retrieval. No packages were installed and no credentials were accessed.
