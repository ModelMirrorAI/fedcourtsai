# Retrieval record

No lookup sought this petition's disposition or subsequent history. No other cell's prediction or evaluation was read. The source baseline was the provisioned August 17, 2026 snapshot and accompanying documents; the quantitative reference was the committed statpack.

## Corpus and setup commands

The initial `uv run fedcourts paths --court scotus --docket 9026000061 --event evt-order-call-for-response-disposition --role predictor` and `uv run fedcourts query --help` attempts failed before execution because the default uv cache was read-only. Retrying with `UV_CACHE_DIR=/tmp/uv-cache` and `uv run --no-sync` succeeded. The paths command returned the case, corpus and event paths; no evaluator-only file was opened. Help was read twice, the second time with `COLUMNS=160`, to see the filters completely. No corpus transfer line was printed for paths or help.

Every successful corpus command below used the cache override and `uv run --no-sync`; `DECIDED_BEFORE` was unset and context was forward. I nevertheless requested priors before Term 2026. That is a docket-Term filter, not an August 2026 day cutoff, so the first query legitimately returned October 2026 grant records from 2025 dockets, not information about this petition.

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`
   - Transfer: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`.
   - Returned three unrelated prior grant records: U.S. DOGE Service, Corey Duran Berry, and Izuchukwu Ozurumba. No opinion bodies were requested. These were not topical analogues and were not used to calibrate the copyright forecast.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '598 U.S. 508' --decided-before 2026 --limit 2`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`.
   - Intended a known copyright-authority lookup. Returned no rows and warned that only 200 in-scope rows carried reporter citations. This is a coverage limitation, not evidence that the authority does not exist. No retry on another sparse citation filter was made.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 20-142 --decided-before 2026 --limit 1`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
   - Returned Michael Skidmore v. Led Zeppelin, with a recorded October 5, 2020 denial and no opinion body. The returned conference/distribution date was later than its denial date, so those chronology fields were disregarded. A selected single denial is not a base-rate estimate and did not independently move the forecast.

Local quantitative reading used `metrics/statpack.md` and the primary `segments` entries in `metrics/statpack.json`, matching `sal-v4`, Term less than 2026 and band `baseline`. Exact pooling produced 660 grant-family equivalents / 12,913 weighted resolved = 0.0511112832. These were local file reads and arithmetic, with no transfer line.

## CourtListener MCP

One `mcp__courtlistener.search` call: type `o`, court `ca3`, case name `Tanksley v. Daniels`, maximum three results, requesting case name, filing date, citation, opinion identifiers, URL and snippet. It returned **HTTP 429**, daily quota exceeded, with an approximately 11,632-second retry interval. No case text or search results were delivered. No direct CourtListener REST fallback, token discovery, or further MCP retry was attempted.

## General web attempts

The web tool returned no usable results or source text for these calls; none furnished substantive evidence:

1. Search batch: `site.ca3.uscourts.gov Tanksley Daniels 902 F.3d 165 substantial similarity` and `site.ca9.uscourts.gov Skidmore Led Zeppelin 952 F.3d 1051 selection arrangement extrinsic`.
2. Search batch: `Tanksley Daniels 902 F.3d 165 2018 court opinion substantial similarity` and `Skidmore Led Zeppelin en banc March 9 2020 opinion pdf`.
3. Direct open of the official opinion at `https://cdn.ca9.uscourts.gov/datastore/opinions/2020/03/09/16-56057.pdf`.

No source was opened from a search hit. The call did not fetch the live docket, response, later proceedings, or outcome of Yonay's petition. Legal analysis rests on the staged filings and appendix, with the split's independent corroboration explicitly limited.
