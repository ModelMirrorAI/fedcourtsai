# Retrieval record

No lookup sought this petition's disposition, live docket, subsequent history, or another cell's output. The case-level provisioned snapshot, context, document manifest, questions presented, petition excerpts, and appendix excerpts supplied the case record.

## Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '583 U.S. 387' --decided-before 2026 --limit 3`
   - **No rows.** The CLI warned that only 200 in-scope SCOTUS rows carry reporter citations and that the empty result likely reflects citation-column coverage, not the precedent's absence. No sparse-filter retry.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`
   - Returned U.S. DOGE Service, No. 25-1103; Corey Duran Berry, No. 25-7026; and Todd Blanche v. Ozurumba, No. 25-1343. These were unrelated grant-only examples, not substantive comparators or a rate-estimation sample. No opinion bodies were requested. The Term mask admits prior docket-number Terms even when their grant dates fall in 2026; this is a forward cell, so the dates do not breach a retrieval clock.
   - `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 24-1016 --limit 1`
   - Retrieved **RiseandShine Corporation v. PepsiCo, Inc.**, the different case expressly named in the petition's hold request. The row records certiorari granted June 29, 2026, a CVSG dated October 6, 2025, three distributions, and `last_live_polled: 2026-10-28`. Its grant predates the target petition's snapshot. No merits opinion was retrieved, and no outcome of the target petition was returned.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`
   - Failed with `ValueError: the service backend has no client-side connection`. No corpus-wide vintage was obtained and no backend was changed. No transfer-statistics line was emitted.

## CourtListener MCP

- `search(type="o", citation="583 U.S. 387", num_results=2)` attempted to retrieve the general mixed-question precedent **U.S. Bank v. Village at Lakeridge**. Returned **HTTP 429**, daily rate limit exceeded, expected availability in 13,206 seconds. No opinion content was obtained. No retry, credential access, or direct CourtListener REST request.

## Web attempts

- A combined `web.run` search for `site.supremecourt.gov "U.S. Bank" "Lakeridge" "2018" opinion` and `site.supremecourt.gov "RiseandShine" "24-1016"` returned no usable result content.
- A second `web.run` search for `U.S. Bank Lakeridge 583 U.S. 387 2018 Supreme Court opinion clear error` returned no usable result content.
- A `web.run` opening of the official Supreme Court docket URL for **24-1016** returned no usable page content. This was the companion, not the target petition.

No web snippet, docket entry, or opinion text from these attempts informed the forecast. The successful corpus companion lookup, not the failed web attempt, supports the companion grant date.

## Committed context and operational setup

- Consulted `metrics/statpack.md` for modern cert dispositions, originating circuit, paid-segment relist/CVSG/amicus cuts, and the sal-v4 per-Term risk-set table. Consulted `metrics/statpack.json` for exact pooling arithmetic: 660 / 12,913 over baseline risk sets in Terms 2017–2025. These are committed-pack figures; corpus-wide freshness could not be verified through the service backend.
- Ran `fedcourts paths` for this event and `fedcourts query --help` for the structured filters. The first attempts without the cache override failed because `/home/codexcell/.cache/uv` is read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`. Subsequent help reads clarified available filters. These setup/help calls retrieved no case outcomes.
- Read the prediction and tooling schemas and `fedcourts validate --help` for the output contract and offline validation interface.
