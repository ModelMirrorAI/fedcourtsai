# Retrieval record

## Provisioned and repository material

Read the prediction contract, prediction/flags/tooling schemas, the event definition, the case-level November 13 snapshot, document manifest, questions presented, petition, supplemental brief, relevant appellate-opinion portions of the appendix, and context. Used the committed `metrics/statpack.md`, specifically the modern-cert population, circuit, paid-segment relist/CVSG/amicus cuts, and prior-Term sal-v8 reached rates, alongside the frozen cert anchor. No other cell's prediction, evaluation, outcome file, or topic-membership artifact was consulted.

## Corpus and CLI calls

- `uv run fedcourts paths --court scotus --docket 9026000267 --event evt-petition-disposition --role predictor`: initial attempt failed before resolving paths because the default uv cache was read-only. No case information was returned.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000267 --event evt-petition-disposition --role predictor`: succeeded, identifying the case and event paths and expressly withholding the evaluator-only outcome path. No corpus transfer line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`: read the structured-filter help. Repeated with `COLUMNS=150 NO_COLOR=1` and `head -65` to inspect the initially truncated filter descriptions. Neither help call retrieved case rows or printed a transfer line.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '552 U.S. 248' --limit 2`: looked up the LaRue precedent by its own citation. Returned no rows and warned that only 195 SCOTUS rows carry reporter citations, so an empty result is primarily a coverage limitation, not evidence that a precedent does not exist. Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.

## CourtListener MCP

- `search(type="o", citation="169 F.4th 459", num_results=2)`: sought the Fourth Circuit's Trauernicht opinion, not this petition's disposition. Returned count zero, query ID `93d1a570`.
- `search(type="o", citation="100 F.4th 386", num_results=1)`: sought the Second Circuit's Cedeno opinion. Returned count zero, query ID `4743c702`.

## Web

One batched `web.run` search attempted the following primary-source lookups:

- `site.supremecourt.gov opinions LaRue DeWolff 552 248 individual account 2008`
- `site.ca4.uscourts.gov Trauernicht Genworth 169 459 2026`

The tool returned no usable result text or source references. No page was opened, no forecast surfaced, and no outside factual claim was taken from these searches. Neither query sought Capital Group v. Pover's disposition.

## Validation

Run the cell-local command with the cache workaround: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000267/events/evt-petition-disposition/predictions/codex-baseline/20261113T042228Z`. This is an artifact check, not a lookup of the case outcome.
