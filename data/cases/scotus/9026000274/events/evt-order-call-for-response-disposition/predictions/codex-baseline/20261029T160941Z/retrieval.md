# Retrieval beyond the provisioned record

No lookup sought this petition's disposition, later docket entries, or decision coverage. No other cell's forecast or evaluation was read. No material under data/qp-topics/ was read.

## Corpus and statistical context

- Read the committed metrics/statpack.md, especially the modern discretionary-cert disposition section, paid-scored-segment relist/CVSG/amicus cuts, and the sal-v4 per-Term reached-band table. Read selected corresponding fields in metrics/statpack.json to compute the OT2017–OT2025 baseline pool: 660 / 12,913 = 0.0511112832. These are checkout artifacts, not a fresh corpus-wide inventory. No corpus-wide freshness claim is made.
- CLI discovery: `uv run fedcourts query --help`, then the same help with `COLUMNS=160`, both with `UV_CACHE_DIR=/tmp/uv-cache`; both succeeded. The repeated help changed display width only.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era roberts --decided-before 2026 --limit 4`. Refused locally because `roberts` is not a decade-token era. The CLI supplied the closed vocabulary. No transfer line was printed.
- Corrected to `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4`. Succeeded, returning scotus/73281386 (25-1103), scotus/73283862 (25-7026), scotus/73500246 (25-1343), and scotus/73281619 (25-1131). These are broad disposition/era examples, not subject-matched legal precedents; no opinion bodies were requested. The returned grant dates included October 13, 2026 and October 1, 2026. The Term filter is coarser than the baseline day; this cell is forward, and these rows supplied no own-case outcome information. They did not determine the forecast.

Exact transfer line for the successful query:

```text
ranged corpus reads: 34 GET(s), 8716288 byte(s)
```

## General legal-context lookups

1. Web search call containing two queries: `United States Hart 635 F.3d 850 2011 Mannava 2422 2251 double jeopardy` and `site.supremecourt.gov opinions Barrett United States 2026 607 128 double jeopardy`. No usable visible result content was returned to the cell.
2. CourtListener MCP `search(type="o", citation="565 F.3d 412", num_results=2)`, seeking Mannava rather than this petition. Returned HTTP 429, with a message that the daily rate limit was exhausted and an estimated wait of 9,159 seconds. No opinion was retrieved. Did not retry or attempt direct REST access.
3. Web search call containing two queries: `site.supremecourt.gov "Barrett" "2026" "Double Jeopardy"` and `site.ca6.uscourts.gov "635 F.3d 850"`. No usable visible result content was returned to the cell.
4. Web open of `https://www.supremecourt.gov/opinions/25pdf/24-5774new_f20h.pdf`, an attempted official-source Barrett opinion retrieval. No usable visible PDF content was returned. Its identity and contents were not verified and it was not used as evidence.

No external case text entered the forecast from these attempts. The petition's descriptions of Mannava, Hart, and Barrett remain attributed to the provisioned materials, not independently verified.

## Local contract and path checks

Read AGENTS.md, .github/prompts/predict.md, the prediction/tooling/flags schemas, and relevant path/serialization helpers. The initial `uv run fedcourts paths --court scotus --docket 9026000274 --event evt-order-call-for-response-disposition --role predictor` failed because the default uv cache was read-only. Repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and named the case and event paths without exposing an outcome. These were local setup operations, not live docket retrieval. Local validation is reported separately from substantive retrieval.

Validated the three JSON outputs with their repository Pydantic models and serialized all seven outputs through fedcourtsai.serialize. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data` passed: `OK: 29704 artifact(s) valid, 71066 reference(s) consistent`.
