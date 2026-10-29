# Retrieval log

## Provisioned inputs and stable references

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction and tooling
schemas, `metrics/statpack.md`, and the relevant sal-v4 Term/band fields in
`metrics/statpack.json`. Read the cell's event definition, context, October 5
snapshot, document manifest, questions presented, and relevant petition and
appendix sections. The supplied documents are the source for the legal
analysis. No other cell's prediction or evaluation, outcome record, or
`data/qp-topics/` artifact was read.

## Corpus commands, including unsuccessful attempts

1. `uv run fedcourts paths --court scotus --docket 9026000377 --event evt-order-call-for-response-disposition --role predictor`
   failed before running because the default uv cache directory was read-only.
2. `uv run fedcourts query --help` failed for the same cache reason.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000377 --event evt-order-call-for-response-disposition --role predictor`
   succeeded and resolved the case and event paths. It did not retrieve an
   outcome.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded and
   displayed structured filters and supported transports.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition granted --limit 3`
   was rejected because `modern` is not a supported decade token; it made no
   successful corpus retrieval and printed no transfer line.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`
   returned U.S. DOGE Service v. U.S. District Court for D.C. (25-1103),
   Corey Duran Berry v. United States (25-7026), and Blanche v. Ozurumba
   (25-1343). The returned rows show grants recorded October 13, 2026 on
   prior-docket-Term cases. This is a forward cell; the Term filter does not
   promise that every returned grant predates the snapshot. None concerns
   Parasmo or supplies this case's outcome. These are generic procedural
   context, not a matched harmless-error sample, and were not used to estimate
   a numerical rate.

   `ranged corpus reads: 28 GET(s), 7340032 byte(s)`

7. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '527 U.S. 1' --decided-before 2026 --limit 1`
   returned no rows. Its coverage note reported only 200 in-scope SCOTUS rows
   carrying reporter citations and warned that empty results likely reflect
   sparse metadata. No opinion body was retrieved and no absence inference
   was drawn.

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

## CourtListener MCP

- `search(type="o", citation="58 F.4th 1308", num_results=2)` attempted
  retrieval of United States v. Kahn. It failed with HTTP 429: daily rate
  limit exceeded. No opinion or search results were returned. No REST
  fallback was attempted.

## Web attempts

- One `web.run` search call contained two general-precedent queries:
  `site.supremecourt.gov opinions 21pdf Ruan 20-1410 subjective knowingly intentionally`
  and `site.ca10.uscourts.gov Kahn 58 F.4th 1308 harmless Ruan`.
  The tool returned no usable content or source references.
- One `web.run` open attempted the official Ruan opinion at
  `https://www.supremecourt.gov/opinions/21pdf/20-1410_1an2.pdf`.
  It likewise returned no usable content or source references.

No search for this petition's disposition, current docket, subsequent history,
or later response was attempted. No retrieved source supplied its outcome.

## Local arithmetic and validation

A local Python calculation used only the committed statpack's baseline
`prefix_est_grant_rate` and `prefix_weighted_resolved` fields for OT2017-2025:
660 / 12,913 = 0.0511112832. This was not a live corpus aggregate. Repository
path/serialization helpers and output schemas were inspected for writing and
validation only. Local schema checks and `uv run fedcourts validate data`
are output checks, not additional factual retrieval.
