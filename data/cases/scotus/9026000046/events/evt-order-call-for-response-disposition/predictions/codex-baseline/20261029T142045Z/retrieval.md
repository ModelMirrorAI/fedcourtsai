# Retrieval record

## Baseline and local context

Read the task contract, prediction/tooling schemas, event definition, provisioned context and September 9 snapshot, document manifest, questions presented, petition argument, and appended Second Circuit summary order. Read the committed `metrics/statpack.md` cert sections and relevant fields in `metrics/statpack.json`; computed the 2017-2025 sal-v4 baseline reached pool as 660 / 12,913. These were local committed base-rate inputs, not a live corpus aggregate. No other prediction, evaluation, outcome file, or labeling-measurement artifact was read.

## Corpus commands

Commands were run through `uv run`, with `UV_CACHE_DIR=/tmp/uv-cache` after the default cache location proved read-only.

1. `uv run fedcourts query --help`, followed by two narrower help-display invocations, to inspect the structured query options. No corpus retrieval from help.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`
   - `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - Returned grants in U.S. DOGE Service (25-1103), Corey Duran Berry (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343). No opinion bodies. The clock is October-Term based, not a January 1 date filter. These were heterogeneous prior-Term grant examples, not arms-ban analogues; none drove the case-specific assessment or an empirical rate.
3. `uv run fedcourts query --court scotus --citation '577 U.S. 411' --decided-before 2026 --full --limit 1`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - No rows. Explicit coverage warning: only 200 SCOTUS rows in scope carry reporter citations; absence through this sparse column does not imply absence of the precedent. No opinion body retrieved.
4. `uv run fedcourts corpus-info`
   - Failed: the service backend has no client-side connection; only query/open-events forward to the service. No vintage or aggregate result obtained. No transfer line was printed. No attempt to pull the full corpus or obtain credentials.

Operationally, `uv run fedcourts paths --court scotus --docket 9026000046 --event evt-order-call-for-response-disposition --role predictor` first failed on the default read-only uv cache, then succeeded with the temporary cache override. It identified paths, not any outcome. Local schema/path/serialization code was inspected for artifact construction only.

## CourtListener MCP

- `search(type="o", citation="577 U.S. 411", num_results=2)` attempted to identify Caetano, a historical precedent, not this petition's outcome. Returned HTTP 429: daily rate limit exceeded. No case content retrieved. No REST fallback or credential extraction attempted.

## Web attempts

The web tool supplied no readable results or source identifiers for any of the following calls; no substantive information was obtained from them:

1. Search: `site.supremecourt.gov opinions 2015 Caetano 14-10078 stun guns common use`.
2. Open: `https://www.supremecourt.gov/opinions/15pdf/14-10078_aplc.pdf`.
3. Combined searches: `site.supremecourt.gov "Wolford" "2026" opinion` and `Caetano Massachusetts 577 U.S. 411 2016 per curiam stun guns`.
4. Open attempted official-opinion path: `https://www.supremecourt.gov/opinions/25pdf/24-1046_nmio.pdf`. This unverified path returned no readable content and is not evidence of an opinion's existence or contents.
5. Open: `https://supreme.justia.com/cases/federal/us/577/411/`.

These attempts concerned general precedents identified in the provisioned petition. I made no search for Calce's disposition or subsequent history, and did not open its current docket or later filings. The petition's own descriptions of Wolford and Viramontes remain uncorroborated supplied advocacy, as noted in `reasoning.md`.
