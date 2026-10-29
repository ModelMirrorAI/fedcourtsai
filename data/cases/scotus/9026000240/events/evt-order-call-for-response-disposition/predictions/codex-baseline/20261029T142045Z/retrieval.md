# Retrieval record

## Corpus and repository context

- Read the required AGENTS.md, predict prompt, prediction and tooling schemas, the cell's event and provisioned record, and selected path/serialization helper definitions. Listed record filenames and checked for scoped AGENTS.md files without reading another cell's outputs or data/qp-topics. The only substantive case input was the provisioned record described in reasoning.md.
- `uv run fedcourts paths --court scotus --docket 9026000240 --event evt-order-call-for-response-disposition --role predictor` failed before running because the default uv cache was read-only. Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000240 --event evt-order-call-for-response-disposition --role predictor`; succeeded and identified the event path. No outcome file was opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`: read structured-filter help.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --limit 3`: rejected the invalid era token `modern` and printed the accepted decade vocabulary. No prior rows or ranged-read statistics were returned.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`: succeeded. Stderr: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`. Returned U.S. DOGE Service v. United States District Court (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche, Attorney General v. Izuchukwu Ozurumba (25-1343). No opinion bodies were requested or returned. These grant-selected rows are non-topical and did not inform the legal assessment or produce a base rate. This is a forward cell; the extra Term filter was conservative, not a representation that its returned grants predated the snapshot cutoff. No target-case query was made.
- Read the modern-cert, paid-segment relist, CVSG, amicus, originating-court, and sal-v4 segment sections of committed `metrics/statpack.md`; inspected top-level keys and segment data in `metrics/statpack.json`. Used jq to pool baseline reached rates over all displayed Terms 2017–2025: 660 estimated grants / 12,913 weighted resolved = 0.0511112832. No live corpus refresh or corpus-wide freshness measurement was performed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate --help`: read the offline validation interface. Output validation itself is a file-integrity check, not a source of case facts.

## External retrieval attempts

- One web search call with two general primary-source queries: `site.supremecourt.gov Rule 11 certiorari before judgment imperative public importance` and `site.supremecourt.gov opinions Carson Makin Locke Davey 2022 religious instruction`. The tool returned no visible results or readable content. No case-specific outcome search was made.
- One web open attempt for `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. The tool returned no visible content. No rule text was taken from this attempt; the petition's own Rule 11 discussion was the available source.
- CourtListener MCP `search(type="o", citation="596 U.S. 767", num_results=1)` attempted a general Carson v. Makin precedent lookup. Returned HTTP 429, daily rate limit exceeded, with no opinion text. No further request or direct REST fallback was attempted.

No external substantive text, this petition's disposition, or another cell's forecast was obtained.
