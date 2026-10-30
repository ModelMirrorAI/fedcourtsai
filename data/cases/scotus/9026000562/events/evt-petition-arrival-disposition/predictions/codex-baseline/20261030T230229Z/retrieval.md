# Retrieval log

No search sought this petition's disposition or subsequent history. No other prediction or evaluation was read. All case-specific facts came from the provisioned record.

## Local context and tooling

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; inspected the provisioned case files and relevant petition/appendix passages.
- Read `metrics/statpack.md`, particularly the sal-v4 per-Term reached-rate table, paid-segment relist/CVSG cuts, and amicus-count cut. The arrival anchor used is the frozen `context.json` value, 0.050890782339271884.
- Initial `uv run fedcourts paths --court scotus --docket 9026000562 --event evt-petition-arrival-disposition --role predictor` and `uv run fedcourts query --help` both failed because `/home/codexcell/.cache/uv` was read-only. Retried both successfully with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`. Paths confirmed the event location and identified the outcome as evaluator-only; no outcome was opened. Help described the structured query surface. No packages were installed.

## Corpus lookups

All query commands used `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1`.

1. `uv run fedcourts query --court scotus --disposition denied --era modern --limit 3`: rejected because `modern` is not a decade token. The CLI supplied the valid vocabulary; no transfer line was printed.
2. `uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`: returned *Google LLC v. VirtaMove, Corp.*, No. 25-1230; *Hastings College Conservation Committee v. California*, No. 25-1231; and *Ryan O'Donnell v. City of Chicago*, No. 25-1098. Each was denied October 19, 2026. Distribution counts were 2, 2, and 4; no opinion bodies were returned. These are not close question-presented comparators and were not used to calculate a rate.
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
3. `uv run fedcourts query --court scotus --citation '406 S.E.2d 356' --decided-before 2026 --limit 1`: no rows. This was not a successful lookup of the state precedent: the query was scoped to SCOTUS and the CLI warned that only 200 scoped rows carried reporter citations. No substantive absence was inferred; the state case was obtained through MCP instead.
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`

## CourtListener MCP

1. `search(type="o", citation="406 S.E.2d 356", num_results=2)`: returned broad, irrelevant matches, including *Davis v. Hulsing Hotels N. Carolina* and *In re Reynolds*. No reliance on those opinions; no pagination requested.
2. `search(type="o", case_name="Key v. Currie", court="sc", num_results=3, fields=["caseName","dateFiled","citation","absolute_url","opinions"])`: one result, *Key v. Currie*, July 8, 1991, 305 S.C. 115, 406 S.E.2d 356, opinion ID 1354673.
3. `read_document(opinion_id=1354673)`: full short opinion, 1,444 characters of returned markup. It declines original jurisdiction where the matter can proceed in trial court absent an extraordinary reason. Used to interpret the authority cited in the provisioned May 21 order, not to determine this petition's outcome.

## Web attempts

Each following `web.run` invocation returned no usable content or source reference. No assertion or quotation is attributed to a successful web result.

1. One search call with three queries: `site.supremecourt.gov Rule 10 considerations governing review certiorari`; `site.uscode.house.gov 28 USC 1257 final judgments highest court state`; `site.sccourts.org Rule 245 original jurisdiction Key Currie public interest special ground`.
2. Search: `site.supremecourt.gov "Rule 10" "compelling reasons"`.
3. Search: `site.sccourts.org "Rule 245" "public interest"`.
4. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
5. Repeated that same rules-guidance open; again no content returned.
6. Find `compelling reasons` at `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`; no content returned and no existence or contents of that URL were assumed.

## Validation

The required repository data validator is run after writing these output files. Its success or any unresolved failure is reported in the completion message; validation does not supply prediction evidence.
