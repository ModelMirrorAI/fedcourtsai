# Retrieval record

## Local reference material and command setup

- Read the prediction contract, repository instructions, prediction and tooling schemas, the event definition, and the provisioned context, snapshot, document manifest, questions presented, petition, and relevant appendix material. No other prediction or evaluation was read.
- Consulted the committed `metrics/statpack.md` cert disposition, circuit, relist, CVSG, amicus and per-Term salience-band sections, with `metrics/statpack.json` for exact prior-Term reached-rate arithmetic. The 2017-2025 baseline pool is 660/12,913 = 0.0511113. No live-corpus population estimate is asserted.
- Initial `uv run fedcourts paths --court scotus --docket 9026000107 --event evt-order-call-for-response-disposition --role predictor` failed before execution because the default uv cache was read-only. Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; path resolution succeeded. The evaluator-only outcome file was not opened.
- Initial `uv run fedcourts query --help` failed with the same cache error. Repeated successfully with `UV_CACHE_DIR=/tmp/uv-cache`; subsequent help reads inspected the available flags. These help/path commands perform no substantive prior lookup and emitted no ranged-read statistics.

## Corpus prior lookup

Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`

Transfer line: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`

Returned three granted rows: scotus/73281386 (U.S. DOGE Service), scotus/73283862 (Corey Duran Berry), and scotus/73500246 (Attorney General v. Ozurumba). No opinion body was present or requested. This query selects grants only, so it supplies no grant-rate denominator. Its year argument is a docket-Term filter, not a September 2026 day cutoff; this is a forward cell. These rows were not used as substantive takings precedents, and none concerns this petition. No additional corpus query or open-events call was attempted.

## CourtListener MCP

- `search(type="o", case_name="Pakdel v. City and County of San Francisco", court="scotus", num_results=2, fields=["caseName", "dateFiled", "citation", "cluster_id", "absolute_url", "snippet"])`: failed with HTTP 429, daily rate limit exceeded. No opinion content was returned. No direct REST fallback or token lookup was attempted.

## Web attempts

- Search query: `site.supremecourt.gov opinions 2020 Pakdel San Francisco 20-1212 finality modest`. No source content or results were returned to the cell.
- Search query: `Pakdel San Francisco Supreme Court June 28 2021 opinion pdf finality modest requirement`. No source content or results were returned to the cell.

Both searches targeted general preexisting precedent, not this petition's disposition. No live docket, later filing, outcome page, related-case decision, or commentary about this case was retrieved. Substantive assessment rests on the staged filings and historical pack rather than external opinion text.
