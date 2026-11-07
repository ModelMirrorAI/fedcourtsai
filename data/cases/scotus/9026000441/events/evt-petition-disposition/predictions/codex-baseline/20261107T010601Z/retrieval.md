# Retrieval record

## Provisioned inputs and local reference material

Read the event definition, case-level `context.json`, snapshot `2026-11-07.json`, document manifest, questions presented, petition including its attached lower-court opinions, and `same-question.json`. Consulted the prediction prompt and prediction/tooling/flags schemas. Read the committed `metrics/statpack.md` modern-cert, circuit, relist, CVSG, amicus and sal-v7 reached-band sections; inspected the top-level keys of `metrics/statpack.json`. No evaluator outcome or other cell's output was read.

## Corpus and CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000441 --event evt-petition-disposition --role predictor`: failed before execution because uv's default cache was read-only. No retrieval occurred.
2. `uv run fedcourts query --help`: same uv cache error. No retrieval occurred.
3. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts paths --court scotus --docket 9026000441 --event evt-petition-disposition --role predictor`: succeeded; resolved case, corpus and event paths and marked the outcome evaluator-only. No outcome was opened.
4. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --help`: succeeded; consulted the structured-filter interface. Repeated with `| tail -75` to view remaining options. Help is not a corpus read.
5. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 5`: rejected unknown era `modern`; printed the permitted decade tokens. No prior results or transfer line were returned.
6. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 5`: succeeded; returned Google v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), O'Donnell v. Chicago (25-1098), Utah v. Mullins (25-1115), and Hadley v. South Bend (25-1158). The combined terminal output was truncated, so its original transfer line was not available in the visible result; I do not invent its counts. Repeated the lookup with compact display as item 7.
7. `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 5 | jq -c '{case_id,case_name,docket_number,disposition,distribution_count,originating_court,date_cert_denied}'`: same five results; all denied October 19, 2026, with distribution counts 2, 2, 4, 3 and 3 respectively. Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`.

The Term filter selects prior docket Terms; it does not require calendar-year dispositions before 2026. These October 2026 dispositions predate the November 7 forward forecast. No queried row concerned the target case. The examples do not supply substantive FECA analogues or an unbiased rate estimate; no opinion hydration was requested.

## CourtListener MCP

- `search(type="o", citation="980 F.3d 423", num_results=3, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`: returned count 0 and an empty results list. Sought Anderson, a precedent quoted in the petition, not the target case. No opinion was retrieved; no direct REST fallback was attempted.

## General web attempts

- One `web.run` call with queries `site.supremecourt.gov Rule 10 considerations governing review certiorari` and `site.uscode.house.gov 18 USC 24 health care benefit program public private plan contract`: returned no usable result content or source identifiers.
- One `web.run` open attempt for `https://www.supremecourt.gov/filingandrules/2026rulesofthecourt_web.pdf`: returned no usable content or source identifiers. No outside rule text was relied upon.

Neither web attempt sought this petition's disposition. No outcome-revealing material was encountered. Forecast-specific legal analysis uses the supplied petition and its appendix rather than claiming successful external verification.
