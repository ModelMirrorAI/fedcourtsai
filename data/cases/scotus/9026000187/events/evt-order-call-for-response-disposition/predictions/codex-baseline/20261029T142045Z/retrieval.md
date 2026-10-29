# Retrieval record

No lookup sought this petition's disposition, subsequent history, or another cell's output.

## Corpus and precedent retrieval

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2010s --citation '576 U.S. 389' --limit 2`
   - Returned no case rows. The diagnostic said only 200 in-scope SCOTUS rows carry any reporter citation and explained that a sparse citation column can produce an empty lookup. This is a coverage limitation, not a finding that Kingsley does not exist.
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
2. Web search: `site.supremecourt.gov opinions 2014 Kingsley Hendrickson 14-6368 objective`.
   - No usable results or source text returned. No case-specific search was made and no external legal assertion was taken from this call.
3. CourtListener MCP `search`, with `type="o"`, `citation="576 U.S. 389"`, `num_results=1`, and fields `caseName`, `dateFiled`, `citation`, `opinions`, `absolute_url`.
   - Refused with HTTP 429. The server reported a 1,400/day limit and an expected wait of 12,633 seconds. No opinion or case facts returned. No retry or direct REST fallback was attempted.

## Committed context and local operations

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist/CVSG/amicus cuts, and the sal-v4 per-Term band table. Read the relevant `terms[].segments` values in `metrics/statpack.json`; pooled the baseline reached numerators and denominators for 2017–2025 with jq, obtaining 660/12,913 = 0.0511112832. These were committed artifacts, not a new live aggregate query.
- Read the prediction, tooling, and flags schemas, AGENTS.md, the predict prompt, and local path/serialization helpers. These were contract checks, not case retrieval.
- Initial unprefixed `uv run fedcourts paths --court scotus --docket 9026000187 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` both failed before execution because uv's default cache location was read-only. Both succeeded after setting `UV_CACHE_DIR=/tmp/uv-cache`; the paths command resolved this event without exposing an outcome. Repeated query-help reads clarified the structured flags; they did not query the corpus.
- Inspected only the cell's provisioned event, snapshot, context, manifest, questions, petition and appendix for case facts. No live docket, external filing, related-case record, or lower-court opinion beyond the staged appendix was retrieved.
- Local JSON/schema checks and `uv run fedcourts validate data` are output validation, not additional evidentiary retrieval.
