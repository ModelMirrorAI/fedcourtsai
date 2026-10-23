# Retrieval beyond the provisioned record

## Committed base-rate context

- Read `metrics/statpack.md`, its introductory scope and "The merits docket (granted cases)" section only; did not use the cert salience tables.
- Read `metrics/statpack.json`'s top-level keys and `merits` object. Used `jq` to select `2015 <= term < 2025` and sum granted, excluded, parsed, and disturbed counts. Result: 539 granted, 56 separately excluded, 516 parsed, 360 disturbed; disturbed rate 0.6976744186046512. This was committed-pack context, not a live corpus query; no ranged corpus-read line was emitted.

## Web attempts

1. `web.run` search batch:
   - `site.supremecourt.gov Khorrami Arizona 2022 Gorsuch twelve jury Williams dissent`
   - `site.supremecourt.gov Ramos Louisiana 2020 opinion Kavanaugh stare decisis jury Williams`
   The tool surfaced no usable results or page content.
2. `web.run` search: `Khorrami v Arizona 2022 Gorsuch twelve jury Williams Supreme Court`. The tool again surfaced no usable results or page content. No page was opened.

## CourtListener MCP attempts

1. `search(type="o", case_name="Khorrami v. Arizona", num_results=3, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`: zero results, query id `445c1469`.
2. `search(type="o", q='"Khorrami"', court="scotus", num_results=3)`: HTTP 429, reported upstream 300/hour rate limit, approximately 2532 seconds until availability. No opinion content returned. Stopped MCP retrieval; no REST fallback.

These queries concerned general precedent, not this case's outcome. No current docket, later case history, outcome record, other prediction, or labeling artifact was consulted. No `fedcourts query` or `open-events` lookup was made.

## Local contract and path checks

Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction/tooling schemas. Ran `uv run fedcourts paths --court scotus --docket 73282277 --event evt-brief-judgment --role predictor`; the initial invocation could not write its default uv cache, and the same command succeeded with `UV_CACHE_DIR=/tmp/uv-cache`. These were contract/path checks, not retrieval of additional case facts.
