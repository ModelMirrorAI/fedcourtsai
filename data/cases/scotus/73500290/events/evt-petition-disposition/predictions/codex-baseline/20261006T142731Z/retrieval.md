# Retrieval record

## Committed context

- Read `metrics/statpack.md`: modern-cert disposition and originating-circuit tables, paid-segment relist and CVSG cuts, and the sal-v4 per-Term reached-band table.
- Read `metrics/statpack.json` for exact high-band reached rates and weighted denominators for the displayed Terms 2017–2024. Locally computed the weighted pool, 314/898. No individual corpus cases were retrieved.
- Ran `git log -1 --format='%cI' -- metrics/statpack.md`; it returned `2026-09-28T12:02:50Z`. This dates the committed artifact, not the corpus's latest pull.
- Ran `fedcourts paths --court scotus --docket 73500290 --event evt-petition-disposition --role predictor` through `uv run`. The first invocation could not initialize its default cache; a writable temporary cache allowed the retry to succeed. The command returned paths only and did not reveal an outcome.
- No `fedcourts query` or `open-events` calls; therefore no ranged-corpus transfer lines exist to record.

## Web attempts

One `web.run` request submitted two general searches:

1. `site.law.cornell.edu/supremecourt/text/431/720 Illinois Brick`
2. `site.supremecourt.gov Rule 10 considerations governing review certiorari`

The tool returned no usable result content. A subsequent direct-open request for the historical Illinois Brick page also returned no usable content:

`https://www.law.cornell.edu/supremecourt/text/431/720`

Neither attempt sought this petition's disposition or subsequent history, and neither supplied information used in the prediction.

## CourtListener MCP

Called `mcp__courtlistener.search` with `type="o"`, `citation="431 U.S. 720"`, and `num_results=1`. It returned HTTP 429, reporting the daily limit exhausted and an expected wait of 2370 seconds. No opinion or docket content was returned. No retry or REST fallback was attempted.

## Provisioned inputs

The event definition, context, dated snapshot, document manifest, questions presented, and relevant petition/opposition passages were read locally. These are baseline inputs, not additional retrieval. The snapshot's own PDF links were not opened. No target-case live docket, disposition, or subsequent-history search was performed.
