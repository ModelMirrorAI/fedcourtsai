# Retrieval beyond the provisioned inputs

## Committed aggregate context

- Read the merits section and introductory scope information in `metrics/statpack.md`; inspected the matching `merits` object and metadata keys in `metrics/statpack.json`. A heading/row search also displayed unrelated aggregate section headings and counts; no cert table was used as the merits anchor.
- Computed the prior-grant-Term pool with `jq`, selecting `2015 <= term < 2025`: 360 disturbed, 516 parsed, 539 granted; rate 0.6976744186046512. This read only the committed aggregate, not case-level corpus rows.
- Ran `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts corpus-info` to seek the required blob vintage. It failed with a service-backend/no-client-side-connection error. No freshness report or `ranged corpus reads` line was returned.
- No `fedcourts query` or `open-events` call was made, and no ranged prior retrieval occurred.

## General web attempts

The following searches returned no usable response content or search snippets:

1. `site.supremecourt.gov opinions 2020 PennEast 19-1039 2021`
2. `site.uscode.house.gov 15 717f h right eminent domain`
3. `site.supremecourt.gov about biographies current members`
4. `PennEast Pipeline New Jersey 19-1039 opinion June 29 2021`
5. `15 USC 717f h eminent domain`
6. `Current Members Supreme Court biographies`

A direct web open of the Supreme Court's historical *PennEast* PDF, file `opinions/20pdf/19-1039_8n5a.pdf`, also returned no usable content. None of these attempts supplied a factual basis for the forecast.

## CourtListener MCP

1. `search(type="o", case_name="PennEast Pipeline Co. v. New Jersey", filed_before="2022-01-01", num_results=3, court="scotus")`: returned the June 29, 2021 opinion, 594 U.S. 482, opinion ID 4699488.
2. `search_document(opinion_id=4699488, query="categorical", snippet_size=1300)`: read the syllabus and majority passages about the scope of Section 717f(h)'s delegation, particularly slip opinion pp. 11–12. Used as historical legal context, not as a holding on the target compensation question.
3. `search(type="o", citation="440 U.S. 202", filed_before="2020-01-01", num_results=1, court="scotus")`: returned *United States v. Bodcaw Co.*, opinion ID 110026. The search metadata date and the displayed decision-date text differed; only the reported 1979 authority and its substantive text were material.
4. `read_document(opinion_id=110026)`: read the historical opinion on appraisal expenses, constitutional compensation, and statutory litigation-cost exceptions.

No search requested this cell's own disposition, subsequent history, current docket, or eventual opinion. No outcome-revealing target-case material surfaced. The provisioned record and parties' briefs remained the source of target-case facts.

## Contract and environment checks

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction/tooling/flags schemas, and the relevant path and serialization helpers. The initial paths command failed because the default uv cache was read-only; redirecting the cache to `/tmp/fedcourts-uv-cache` succeeded. Resolved the output location using `CasePaths` and `EventPaths`. These were contract checks, not substantive case retrieval.
