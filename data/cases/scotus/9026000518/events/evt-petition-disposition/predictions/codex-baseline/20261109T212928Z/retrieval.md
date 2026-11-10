# Retrieval record

## Provisioned inputs and local reference material

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`. Local listings and instruction-file checks were administrative discovery, not retrieval of case outcomes. An initial overbroad `rg --files` listed many repository paths, including outcome filenames, but did not open their contents. No other prediction, evaluation, outcome file, or labeling-measurement artifact was read.
- Read this cell's `event.yaml`, case-level `record/context.json`, `record/snapshots/2026-11-09.json`, `record/documents/documents.json`, `questions-presented.txt`, and the petition's argument and relevant bound-appendix portions. No separately provisioned BIO, related docket, or lower-court file was present.
- Consulted the committed `metrics/statpack.md`: modern cert population, paid-segment relist/CVSG/amicus cuts, salience bands, originating-circuit table heading/initial rows, and the `sal-v8` per-Term reached-band table. Used the context's frozen 5.158792858% anchor rather than calculating a different anchor from terminal buckets.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000518 --event evt-petition-disposition --role predictor` failed before execution because the default uv cache was read-only. No retrieval or transfer line resulted.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9026000518 --event evt-petition-disposition --role predictor` succeeded, confirming the case and event paths. It did not expose an outcome path or outcome contents. No corpus transfer line.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` succeeded. Read before the first query. No corpus transfer line.
4. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition denied --era roberts --limit 4` was refused with an era-vocabulary usage error; `roberts` is not an accepted decade token. No retrieval or corpus transfer line.
5. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026-11-09 --limit 4` succeeded. Returned Jesse Guardado's petition, two Guardado-related applications, and J. Jesus Lopez Jaime's application, all denied November 5, 2026. These are poorly matched contextual priors, not evidence concerning the target petition; I did not use their disposition mix as an estimated grant rate. Transfer line exactly:

   `ranged corpus reads: 26 GET(s), 6815744 byte(s)`

The optional day bound was used conservatively on this forward cell; it was not an assertion that the cell is a replay. No `--full` bodies or `open-events` calls were requested.

## Web attempts

1. A single `web.run` search call with queries `site.supremecourt.gov opinions Goodyear Haeger 2017 but for sanctions bad faith` and `site.loc.gov "Clinton v. Jones" "705" "706" 520` returned no usable response content.
2. A `web.run` open call for `https://www.govinfo.gov/content/pkg/USREPORTS-520/pdf/USREPORTS-520-681.pdf` likewise returned no usable response content. No fetched web material informed the forecast.

Neither attempt searched the target petition's disposition, subsequent history, or coverage of its decision.

## CourtListener MCP calls

1. `search(type="o", citation="520 U.S. 681", num_results=1)` returned Clinton v. Jones, May 27, 1997, including opinion ID 118115. This is general preexisting precedent, not the target litigation.
2. `search_document(opinion_id=118115, query="timing and scope", snippet_size=800)` returned the passage explaining presidential case-management accommodation while rejecting a categorical term-long stay. Used to qualify, not eliminate, the distinction between a President as defendant and as private plaintiff.
3. `search(type="o", citation="581 U.S. 101", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])` returned Lewis v. Clarke, 581 U.S. 155 (2017), instead of the intended Goodyear opinion. Discarded as nonresponsive; no additional opinion was opened. Goodyear's relevance is described as the petition's argument, not as independently verified by that search.

No CourtListener query concerned this petition's own Supreme Court docket or disposition. No outcome-revealing target material surfaced. Final cell validation is an output-schema/completeness check, not substantive retrieval.
