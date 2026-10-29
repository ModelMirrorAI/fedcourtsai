# Retrieval record

No lookup sought this petition's disposition, later filings or subsequent history. The forecast uses the September 30 provisioned baseline rather than a refreshed live docket. No other prediction/evaluation outputs or topic-labeling artifacts were read.

## Local reference material and setup

- Read `AGENTS.md`, `.github/prompts/predict.md`, prediction/tooling/flags schemas, the event definition, snapshot, context, document manifest, questions presented, petition passages and appendix opinion/district-court passages.
- Consulted `metrics/statpack.md` and `metrics/statpack.json`. Computed the OT2017-OT2025 baseline reached pool locally: 660 estimated grant-family outcomes over 12,913 weighted resolved petitions, 5.1111%.
- `uv run fedcourts paths --court scotus --docket 9026000208 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` initially failed because uv's default cache was read-only. Both succeeded with `UV_CACHE_DIR=/tmp/uv-cache`. The paths command did not expose an outcome.
- Inspected the package's path/ID and serialization helpers solely to resolve and serialize this cell's output. An initial Python introspection attempted a nonexistent module-level `paths.prediction_dir` and failed; the method exists on the event-path object.

## Corpus lookup attempts

All successful commands below used the cell's configured service backend and `UV_CACHE_DIR=/tmp/uv-cache`.

1. `uv run fedcourts query --court scotus --era modern --disposition denied --decided-before 2026 --limit 3`
   - Refused: `modern` is not a decade token. The diagnostic supplied the valid vocabulary. No corpus rows or transfer line returned.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3`
   - `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Returned Google/VirtaMove (25-1230), Hastings College Conservation Committee (25-1231), and O'Donnell/Chicago (25-1098), all unrelated denials. Not used as substantive comparators. The Term clock does not imply a strict calendar-year decision cutoff for forward retrieval.
3. `uv run fedcourts corpus-info`
   - Failed: the service backend has no client-side connection. No corpus-wide pull/snapshot vintage returned. No attempt to obtain credentials or change backend followed.
4. `uv run fedcourts query --court scotus --docket-number 20-1505 --decided-before 2026 --limit 1`
   - `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Returned Merchant/Mayorkas, denied June 28, 2021; one distribution. Used only as historical issue-context evidence of prior reluctance to grant. Pull stamps were not available under the clock.
5. `uv run fedcourts query --court scotus --docket-number 20-1043 --decided-before 2026 --limit 1`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned United States/Cano, denied June 28, 2021; two distributions. Same limited use and vintage limitation. Neither query used `--full` or hydrated opinion text.

## CourtListener MCP

- `search(type="o", citation="943 F.3d 713", num_results=2)` for the Fourth Circuit's Aigbekaen opinion.
  - HTTP 429; daily limit exhausted, reported retry in 315 seconds. No opinion retrieved. Did not retry or fall back to REST.

## General web checks

These were checks of general pre-existing legal authorities, not searches for the target petition.

1. One batched search with the three query strings:
   - `site.supremecourt.gov opinions Riley California 2014 cell phone warrant border`
   - `site.ca9.uscourts.gov 17-50190 Cano 2019 border search contraband`
   - `site.ca4.uscourts.gov Aigbekaen 2019 border search nexus warrant`
   - No visible usable results returned. No target-case outcome was surfaced or used. The initial exploratory Cano docket number differs from the one in the subsequent attempted official-opinion fetch; neither supplied evidence.
2. Search: `site.supremecourt.gov "Riley v. California" "13-132" opinion pdf`.
   - No visible usable results returned. No independently usable opinion passage adopted.
3. Open attempt:
   ```text
   https://www.supremecourt.gov/opinions/13pdf/13-132_8l9c.pdf
   ```
   - No usable opinion text returned. No legal proposition rests on this attempted fetch.
4. Attempted to open a Ninth Circuit opinion at:
   ```text
   https://cdn.ca9.uscourts.gov/datastore/opinions/2019/08/16/17-50151.pdf
   ```
   - No visible usable opinion text returned. Did not use this attempted fetch as independent verification. The forecast's description of Cano instead rests on the provisioned petition, pp. 9-11.
5. Find attempt for `Our answer to the question` in the official bound volume:
   ```text
   https://www.supremecourt.gov/opinions/boundvolumes/573bv.pdf
   ```
   - No usable Riley passage returned. Riley's characterization in the forecast is attributed to the provisioned petition instead.

All five web calls returned no visible usable result text. No web result supplied a factual input or independent verification. No quotation from an external opinion is reproduced.
