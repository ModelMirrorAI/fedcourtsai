# Retrieval record

## Provisioned baseline

Read the event definition and all provisioned record files: the November 7 snapshot, context, questions presented, petition with retained appendix, decision below, lower-court docket summary, document manifest, and same-question list. No other prediction or evaluation was read, and no petition-outcome lookup was made. The earlier emergency stay appears in the petition itself and predates this forecast.

## Committed base rates

Consulted `metrics/statpack.md`: modern discretionary-cert dispositions, originating circuit, paid-segment relist/CVSG/amicus cuts, and the sal-v7 Term table. Consulted `metrics/statpack.json` to pool the displayed strictly prior Terms 2017–2025: baseline 652/12,657 and federal 155/212. No 2026 outcomes entered either pool.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000599 --event evt-petition-arrival-disposition --role predictor` — failed before execution because the default uv cache was read-only.
2. `uv run fedcourts query --help` — same cache failure; no corpus access.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000599 --event evt-petition-arrival-disposition --role predictor` — successfully resolved permitted paths; did not open the evaluator-only outcome.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — successful CLI documentation read.
5. `UV_CACHE_DIR=/tmp/uv-cache COLUMNS=160 uv run fedcourts query --help` — repeated help with wider output to read the filtering and clock options.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --decided-before 2026 --limit 4` — completed with no returned rows. Transfer line: **`ranged corpus reads: 1014 GET(s), 265420800 byte(s)`**. This was an empty structured-filter lookup, not a substantive negative precedent. No `--full` hydration was requested.

The cache override allowed the pre-provisioned tooling to run; no package installation was requested. Subsequent polling retrieved the same query's completion, not additional corpus lookups.

## Web attempts

The web tool returned no usable content for these calls. None supplied facts used in the forecast.

1. One batched search call containing these three queries:
   - `site.supremecourt.gov "25-845" "April 27"`
   - `site.supremecourt.gov "Hollingsworth" "reasonable probability" "fair prospect"`
   - `site.supremecourt.gov "Winter" "555 U. S. 7" "balance"`
2. Attempted official order-list open at `https://www.supremecourt.gov/orders/courtorders/042726zor_8mj9.pdf`. No document content returned; the guessed locator is not a verified source.
3. Attempted official *Hollingsworth* PDF open at `https://www.supremecourt.gov/opinions/09pdf/09A648.pdf`. No document content returned.

These were general precedent/comparator checks, not a search for this petition's disposition.

## CourtListener MCP

1. `search(type="o", citation="558 U.S. 183", num_results=1)` — returned *Hollingsworth v. Perry*, decided January 13, 2010, cluster 1747, including lead opinion 9413203. Used only as general stay-standard context.
2. `search_document(opinion_id=9413203, query="reasonable probability", snippet_size=1100)` — one match at the discussion corresponding to 558 U.S. 190. Confirmed the certiorari-prospect, reversal-prospect, and irreparable-harm components of a stay pending certiorari. No direct quotation is reproduced in the output documents.
3. `search(type="o", court="scotus", case_name="Abbott v. League of United Latin American Citizens", filed_before="2026-11-07", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url", "docketNumber"])` — zero results. The petition's asserted comparator was not independently verified and is not a separate factual premise of the probability.

No current Supreme Court docket or subsequent history for this petition was retrieved. No CourtListener REST fallback was used.
