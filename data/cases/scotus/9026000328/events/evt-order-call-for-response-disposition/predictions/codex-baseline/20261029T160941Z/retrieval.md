# Retrieval record

No lookup sought this petition's outcome or subsequent history. No other cell's prediction or evaluation and no labeling-measurement artifact was read.

## Corpus and committed statistical context

- Initial `uv run fedcourts paths --court scotus --docket 9026000328 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` both failed because `/home/codexcell/.cache/uv` is read-only. Repeated both with `UV_CACHE_DIR=/tmp/uv-cache`; both succeeded. Paths was used for path resolution only; no evaluator-only file was opened. Help was consulted twice with the writable cache to read the structured-filter and cutoff options.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3` succeeded. Transfer line: **`ranged corpus reads: 28 GET(s), 7340032 byte(s)`**. Returned three grant-side priors: U.S. DOGE Service v. U.S. District Court for D.C. (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343). They were not close substantive analogues; no body hydration or grant-frequency estimate was made from this grant-only sample. The term filter admits earlier docket-Term grants with calendar-2026 dates; this forward cell has no replay leakage clock.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed: the service backend has no client-side connection and supports query/open-events forwarding instead. No read-stats line was returned and no corpus-wide vintage was obtained. I did not switch transports, seek credentials, or pull/mutate a corpus.
- Read the relevant modern-cert, paid scored-segment relist/CVSG/amicus, and sal-v4 per-Term sections of `metrics/statpack.md`; used exact risk-set fields from `metrics/statpack.json`. A jq aggregation of every displayed prior Term, 2017–2025, produced 660 weighted grants and 12,913 weighted resolutions, rate 0.0511112832. Excluded 2026.
- `git log -1 --format='%cI %h' -- metrics/statpack.json` reported `2026-10-28T17:22:12Z a07205582`. This dates the committed artifact, not the underlying corpus's newest pull or snapshot.

## CourtListener MCP

- One search attempt: type `o`, court `ca3`, query `"Whittaker" "Daniels"`, order `dateFiled desc`, num_results 3, fields caseName/dateFiled/citation/absolute_url/id/opinions. Result: **HTTP 429, daily quota 1400 exceeded**, with an approximately 8,403-second wait. No opinion or snippet was obtained. No REST fallback or additional MCP retrieval was attempted.

## Web searches

Two web tool calls, each containing two queries, were attempted for general preexisting authorities only:

1. `"Rogers v. Guaranty Trust" "288" "130"`; `"Mercantile National Bank" "Langdeau" "371" final judgment 555`.
2. `Rogers v Guaranty Trust Co 288 US 123 1933`; `Mercantile National Bank v Langdeau 371 US 555 1963`.

Both calls returned empty tool responses, with no usable result, URL, opinion text, or citation. No external material was incorporated.

## Provisioned inputs and utilities

Read the named baseline, petition and question, document inventory, selected appendix passages, and staged companion 26-350. A read-only sidecar reviewed the appendix for vehicle obstacles; it made no retrieval calls or writes. I independently checked the operative-scope and preservation passages used in the rationale. Local schema, path, serialization, and validation utilities were consulted solely to satisfy the output contract. No other case documents were fetched.
