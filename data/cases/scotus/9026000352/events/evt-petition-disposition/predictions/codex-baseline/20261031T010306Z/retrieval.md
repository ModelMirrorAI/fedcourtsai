# Retrieval record

## Local references and tooling

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json` for the contract; `metrics/statpack.md` for the cert disposition, originating-court, paid relist, paid CVSG, paid amicus, and sal-v4 band context. Case-specific inputs are the provisioned record and event definition, not external retrieval.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000352 --event evt-petition-disposition --role predictor`. Failed before execution because the default uv cache was read-only.
- Attempted `uv run fedcourts query --help`. Same default-cache failure; no corpus transfer line.
- Retried `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000352 --event evt-petition-disposition --role predictor`. Succeeded and resolved the event path; evaluator-only outcome was not opened.
- Retried `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`. Succeeded and displayed structured filters.

## Corpus priors

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era modern --limit 3`
  - Rejected: `modern` is not a valid decade token; returned the vocabulary and usage guidance. No corpus transfer line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`
  - Succeeded. Returned Google LLC v. VirtaMove, Corp., et al. (25-1230), Hastings College Conservation Committee, et al. v. California, et al. (25-1231), and Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al. (25-1098), all denied October 19, 2026, with distribution counts two, two, and four respectively. No opinion bodies were requested. These are not subject-matched analogues and were not treated as a rate estimate.
  - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`

## Web attempts

- First `web.run` search batch: `site.supremecourt.gov opinions 2023 Murray UBS 601 U.S. 23 whistleblower` and `site.supremecourt.gov Rule 10 certiorari judicial discretion error correction`. Tool returned no usable content or sources.
- Second `web.run` search batch: `Murray UBS February 8 2024 opinion` and `Rule 10 considerations governing review certiorari`. Tool again returned no usable content or sources.
- Neither batch searched for this petition's disposition, and neither supplied facts used in the forecast.

## CourtListener MCP

- `search(type="o", citation="601 U.S. 23", num_results=2)`: succeeded, query ID `bccfde5b`. Returned duplicate records for Murray v. UBS Securities, LLC, docket 22-660, decided February 8, 2024; opinion IDs 11066702 and 9931115. Used to confirm the identity and date of the petition's cited precedent, not this case's outcome.
- `search_document(opinion_id=9931115, query="intent", snippet_size=550)`: failed with HTTP 502; no opinion text obtained. No direct CourtListener REST fallback was attempted. Substantive comparison rests on the provisioned filing and lower-court order instead.

No live lookup of this petition's disposition or subsequent history was attempted. Validation commands are local output checks, not additional factual retrieval.
