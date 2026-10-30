# Retrieval and tooling record

## Provisioned inputs

Read event.yaml; record/context.json; record/snapshots/2026-09-05.json; record/documents/documents.json; questions-presented.txt; the petition's substantive argument; and the relevant appendix portions. These are inputs, not external retrieval. No target-case outcome, live docket, subsequent history, related-case outcome, other cell output, or QP-labeling artifact was sought or read.

## Committed base-rate material

Consulted metrics/statpack.md: modern discretionary-cert disposition and originating-circuit sections; paid scored-segment relist, CVSG, and amicus cuts; and the sal-v4 per-Term risk-set table. Consulted metrics/statpack.json for exact baseline-band reached rates and weighted denominators for every rendered Term before 2026. Pooled 660 / 12,913 = 0.0511112832. The figures describe this committed pack, not a newly refreshed corpus census.

## Corpus service

Initial `uv run fedcourts paths --court scotus --docket 9026000231 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` attempts failed before retrieval because uv's default cache directory was read-only. Reissued with `UV_CACHE_DIR=/tmp/uv-cache`; path resolution and help succeeded. Help was consulted again with a wider terminal to read the structured-filter semantics. No corpus transfer line accompanied the cache failures, path resolution, or help.

Executed one corpus lookup:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 5
ranged corpus reads: 34 GET(s), 8716288 byte(s)
```

Returned five granted prior-Term rows: scotus/73281386 (25-1103), scotus/73283862 (25-7026), scotus/73500246 (25-1343), scotus/73281619 (25-1131), and scotus/73500251 (25-1349). They carried no opinion bodies or usable substantive ACCA analogy. This outcome-selected lookup was not used as a rate estimate. Some decisions were in October 2026 despite earlier docket Terms: the bare year is a Term bar, not a day bar. The target is a different, Term-2026 case and was excluded; this is a forward cell, and no target disposition surfaced.

## General-precedent web searches

Two web.run search calls were attempted, each containing two queries:

1. `site.supremecourt.gov opinions 2024 Delligatti knowingly intentionally bodily injury omission 23-825`
2. `site.supremecourt.gov opinions Borden United States 19-5410 2021`
3. `Delligatti United States 2025 Supreme Court opinion intentional knowing injury omission`
4. `Borden United States 593 U.S. 420 2021 Supreme Court opinion`

Both calls returned no usable result text or source references. No web page was opened and no target-case search was made. No external holding was inferred from these empty results.

## CourtListener MCP

Attempted `search(type="o", case_name="Delligatti v. United States", court="scotus", filed_before="2026-09-05", num_results=3)`.

The MCP server returned HTTP 429, reporting the daily request limit exceeded and an approximately two-hour wait. No opinion or search result was returned. I did not retry, seek credentials, or use a REST fallback. The prediction instead relies on provisioned filings and committed base-rate material.

## Validation

Operational schema and path-helper inspection was limited to constructing and validating the prescribed outputs; it supplied no additional case evidence.
