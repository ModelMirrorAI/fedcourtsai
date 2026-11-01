# Retrieval record

No lookup sought this application's disposition, live docket, subsequent history, or another predictor's output. No CourtListener MCP lookup was made.

## Corpus and local contextual tooling

- `uv run fedcourts paths --court scotus --docket 9526000602 --event evt-motion-disposition --role predictor` failed before execution because the default uv cache was read-only. It returned no case or outcome information. Subsequent uv commands used `UV_CACHE_DIR=/tmp/uv-cache` and no-sync mode; no installation was requested.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9526000602 --event evt-motion-disposition --role predictor` succeeded on three invocations. It resolved the event and corpus paths and marked the outcome evaluator-only. No outcome was opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` was consulted twice, the second time with `COLUMNS=120` and output limited to the opening help section. These calls supplied filter syntax, not corpus rows.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 5` returned five denied cert petitions: scotus/73265705, scotus/73266074, scotus/73281381, scotus/73281394, and scotus/73281642. They were not interim analogues and did not alter the probability. The year filter uses docket/derived Term, so some returned disposition dates fall in October 2026; this forward cell has no replay clock. None is this application.
  Transfer report: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`.
- Read the committed `metrics/statpack.md` interim section and `metrics/statpack.json` interim per-Term counts. A jq calculation over Terms 2016–2025 yielded 160 grants / 1,366 resolved substantive applications = 0.1171303074670571, with 16 unparsed applications. No cert-band table supplied the anchor.

## Attempted web context

The following three web tool calls returned no usable response text or source identifiers. None supplied evidence, citations, or outcome information:

1. Opened the general rules PDF at `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
2. Searched `site.supremecourt.gov Rule 23 stay application relief court below extraordinary circumstances`.
3. Attempted to open `https://www.supremecourt.gov/filingandrules/2026rulesofthecourt_web.pdf`. This candidate filename was not verified and is not relied upon as an existing publication.

The forecast therefore rests on the provisioned record, the committed interim counts, and explicitly identified general legal judgment, not externally recovered application content.
