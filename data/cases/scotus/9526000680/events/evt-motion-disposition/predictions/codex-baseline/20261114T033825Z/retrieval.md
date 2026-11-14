# Retrieval and operational log

## Local context beyond the provisioned case inputs

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, and `schemas/agent_tooling.schema.json` for the contract. Inspected workspace instructions and status without reading any other prediction or evaluation.
- Read the interim section and applicant-class table of `metrics/statpack.md`. Parsed `metrics/statpack.json` using `jq` to pool Terms 2016–2025, check finer unread counts and unparsed coverage, and aggregate applicant cuts. The scoring pool was 156/1,337; the private/unmarked descriptive cell was 63/906.

## Corpus and CLI calls

- `uv run fedcourts paths --court scotus --docket 9526000680 --event evt-motion-disposition --role predictor` failed before execution because the default uv cache was on a read-only filesystem.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --offline --no-sync fedcourts paths --court scotus --docket 9526000680 --event evt-motion-disposition --role predictor` succeeded, identifying the case, corpus location, and event. No outcome file was opened.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --offline --no-sync fedcourts query --help` and a second help invocation with `COLUMNS=180` displayed structured query options. These did not retrieve case records.
- `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --offline --no-sync fedcourts query --court scotus --citation '434 U.S. 1301' --limit 3` returned no case rows. Diagnostic: citation coverage in the SCOTUS scope was sparse, so the empty result was not treated as absence of the precedent. Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.

## Web attempts

- One `web.run` search call attempted two general-precedent searches: `site.supremecourt.gov "Hollingsworth v. Perry" "reasonable probability" "fair prospect"` and `site.law.cornell.edu/supremecourt/text/541/509 "meaningful access"`. The tool returned no usable output or source content.
- One `web.run` open call attempted the Cornell page for 541 U.S. 509. It likewise returned no usable output or source content. No proposition was attributed to either web attempt.

## CourtListener MCP

- `search(type="o", citation="558 U.S. 183", num_results=2)` returned Hollingsworth v. Perry, January 13, 2010, and an unrelated result. Used only the matching precedent.
- `search_document(opinion_id=1747, query="reasonable probability", snippet_size=850)` returned the passage setting out the three requirements for a stay pending certiorari and balancing of equities. Used its legal standard, not its case-specific odds or coalition.
- `search(type="o", court="scotus", citation="420 U.S. 469", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url"])` returned an unrelated Hydro Aluminium result. It was not relied on; the citation search was corrected with a case-name filter.
- `search(type="o", court="scotus", case_name="Cox Broadcasting Corp. v. Cohn", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url"])` returned Cox Broadcasting, March 3, 1975, including the majority opinion identifier 9426016.
- `search_document(opinion_id=9426016, query="seriously erode", snippet_size=1100)` returned the majority's discussion of the fourth finality category. Used to assess, not conclusively reject, the applicant's asserted exception.

No own-case outcome, later own-case docket, other forecast, or related-case disposition was sought. The 2026 Malliotakis decision was mentioned only in the provisioned application and was not independently retrieved. Validation is a local contract check, not legal-evidence retrieval.
