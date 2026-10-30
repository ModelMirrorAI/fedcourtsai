# Retrieval log

No search or query sought this petition's Supreme Court disposition,
subsequent history, another prediction, or labeling artifacts.

## Corpus and CLI calls

All successful `uv` invocations used `UV_CACHE_DIR=/tmp/uv-cache`; the default
cache location is read-only in this runner.

1. `uv run fedcourts paths --court scotus --docket 73279493 --event evt-order-call-for-response-disposition --role predictor`
   initially failed because the default uv cache was read-only. Reissued with
   the cache override: returned the case id, corpus path and event path;
   the outcome location was withheld as evaluator-only.
2. `uv run fedcourts query --help` initially failed at the same cache step.
   Reissued with the cache override: returned structured-filter help.
3. `uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2025 --limit 3`
   failed because `modern` is not a valid era token. No rows or transfer line.
4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2025 --limit 3`
   returned RiseandShine v. PepsiCo (24-1016), Chaney v. United States
   (24-6543), and Monsanto v. Durnell (24-1068). These are unrelated
   grant-side records, not bankruptcy comparators; no opinion bodies were
   requested and no grant-rate inference was drawn. The bare-year mask
   admitted prior docket Terms, including rows with later grant dates; these
   rows did not inform the case-specific forecast.
   `ranged corpus reads: 72 GET(s), 18874368 byte(s)`
5. `uv run fedcourts query --court scotus --citation '523 U.S. 57' --decided-before 2025 --limit 1`
   returned no rows. The coverage note reported only 200 citation-bearing
   SCOTUS rows in scope and cautioned that absence was likely a metadata gap.
   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
6. `uv run fedcourts corpus-info` failed: the service backend has no
   client-side connection. No corpus-wide vintage was available from it.

## CourtListener MCP

- `search(type="o", citation="290 F.3d 1140", num_results=1,
  fields=["caseName", "citation", "dateFiled", "absolute_url", "cluster_id", "id", "snippet"])`
  attempted to verify In re Su. Returned HTTP 429, daily rate limit exhausted,
  expected availability in 2,267 seconds. No opinion or result was obtained.
  No direct REST fallback was attempted.

## Web

One `web.run` call contained two general searches:
- `"In re Su" "290 F.3d 1140" subjective`
- `"In re Berge" "953" "907" malicious`

The tool returned no usable results, sources, or text. No case outcome was
exposed and no web-derived factual assertion was used.

## Local reference material

Read the committed `metrics/statpack.md` modern-cert, paid-segment relist,
CVSG, amicus and sal-v4 Term-band sections. Used `metrics/statpack.json`
for exact prior-Term prefix-rate pooling: 607 / 11,599 = 0.0523321 for
baseline reached, Terms 2017–2024. These are committed-pack figures, not a
fresh corpus census. Also inspected the output schemas and the repository's
path, serialization and prediction-model helpers for contract compliance.
