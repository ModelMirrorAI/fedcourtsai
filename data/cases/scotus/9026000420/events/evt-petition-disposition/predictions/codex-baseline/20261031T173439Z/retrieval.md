# Retrieval record

## Local inputs and tooling

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the tooling and flags schemas, the specified event definition, the case-level snapshot `2026-10-31.json`, `context.json`, `same-question.json`, `documents/documents.json`, `questions-presented.txt`, and the petition's argument and relevant appendix sections. Consulted the committed `metrics/statpack.md`, especially the modern-cert, circuit, paid-segment relist/CVSG/amicus, and sal-v6 reached-rate tables. No other prediction or evaluation was read. No labeling artifacts were read.

Initial attempts at `uv run fedcourts paths --court scotus --docket 9026000420 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help` failed before execution because the default uv cache path was read-only. Reissued both successfully with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache` and `uv run --no-sync`; no packages were installed. The paths command confirmed the case and event paths. Help documented structured filters. Other shell operations inspected local inputs/schemas, checked working-tree status and patch-tool availability, and validated the resulting output; they did not retrieve a case outcome.

## Corpus calls

All successful query commands used the same cache override and `--no-sync`. No replay clock is supplied in this forward cell.

1. `uv run --no-sync fedcourts query --court scotus --disposition denied --era 2020s --limit 4`
   - Returned Louisiana v. Devon Energy, No. 26A499; Griffin v. Isaac, No. 26A535; Monte v. United States, No. 26A532; and Schultz v. Bokf, No. 26A555. All were substantive applications, not suitable cert comparators; no adjustment was drawn from their denials. The first tool response was truncated and its read-statistics line was not visible in the retained response.
2. `uv run --no-sync fedcourts query --court scotus --docket-number 26-1 --limit 1`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Sunoco v. Cline: denial dated October 5, 2026; one distribution. Used only as another case's status, correcting the petition's earlier description of it as pending.
3. `uv run --no-sync fedcourts query --court scotus --docket-number 25-677 --limit 1`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - City of Cleveland v. Pickett: unresolved, four distributions, last polled October 26, 2026. Used as limited evidence of another potentially overlapping petition, not a granted lead case.
4. Repeated the exact command in item 1, with output reduced to case identifiers, captions, docket numbers, dispositions, dates, distribution counts, and application kind for readability.
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Same four application rows, served from cache; no new substantive evidence.

## CourtListener MCP

- `search(type="o", citation="175 F.4th 172", num_results=3)`: zero results. This was a lookup of the published lower-court companion opinion, not the Supreme Court petition's disposition. Relied instead on the provisioned appendix. No REST fallback was attempted.

## Web attempts

Every web call below returned no usable content or visible result payload. None contributed substantive evidence, and no result about this petition's disposition surfaced.

1. One search call containing both queries: `site.supremecourt.gov opinions 2024 Laboratory Corporation Davis Kavanaugh 24-304 dismissed` and `site.supremecourt.gov opinions TransUnion Ramirez standing damages 2021 20-297`.
2. One search call containing both queries: `site.supremecourt.gov "LABORATORY" "24–304"` and `site.supremecourt.gov "TRANSUNION" "594" "413"`.
3. Attempted official opinion PDF open: `https://www.supremecourt.gov/opinions/20pdf/594us2r59_197d.pdf`. The path was an attempted source location, not a successfully verified citation.
4. Attempted official prior-case docket open: `https://www.supremecourt.gov/docket/docketfiles/html/public/24-304.html`.
5. Repeated the same official prior-case docket open after the empty response; again no usable content.

No query or page request sought the disposition or subsequent history of Jack Rabbit's Supreme Court petition, No. 26-420.
