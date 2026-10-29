# Retrieval record

## Provisioned and committed material

Read the event definition, November 7, 2025 snapshot, context, document
manifest, question presented, petition's substantive arguments, relevant
appendix decisions and rehearing order, and October 8 party letter. Beyond
those provisioned case inputs, read the committed `metrics/statpack.md`
cert-disposition, circuit, relist, CVSG, amicus, and salience-band sections.
Inspected the matching JSON's keys and Term structure, then computed the
baseline risk-set pool using only OT2017-OT2024. No corpus snapshot freshness
or current case-state claim is made from those artifacts.

## Corpus calls, including setup failures

1. `uv run fedcourts paths --court scotus --docket 73277388 --event evt-order-call-for-response-disposition --role predictor`
   failed before running because uv's default cache location was read-only.
   Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; returned the case, corpus and
   event paths, without an outcome path or outcome content.
2. `uv run fedcourts query --help` failed with the same uv cache error.
   Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`.
   Also displayed its filter section with
   `COLUMNS=150 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help`.
   These were CLI help reads, not corpus data queries.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 3`
   returned RiseandShine/PepsiCo (24-1016), Chaney (24-6543), and
   Monsanto/Durnell (24-1068), none this case. Their decision stamps extended
   beyond this snapshot: the bare-year filter selects prior docket Terms,
   not decisions strictly preceding this day. This is a forward cell with
   no mandatory replay clock, but these selected, unrelated grants were not
   used as analogues or to estimate grant likelihood. No opinion bodies were
   requested.

   `ranged corpus reads: 72 GET(s), 18874368 byte(s)`

4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 16-32 --decided-before 2025 --limit 1`
   attempted a historical Kindred Nursing docket lookup. It returned
   `scotus/4609876`, docket 16-32, with an empty caption, no opinion, and
   null disposition and decision dates. That establishes no independently
   usable holding; I relied instead on the provisioned petition's discussion
   of Kindred and did not hydrate the row.

   `ranged corpus reads: 653 GET(s), 171180032 byte(s)`

## Web-tool attempts

All three `web.run` calls returned no source references, snippets, or usable
page text. Nothing from them entered the prediction.

1. One search call with two queries:
   - `site.supremecourt.gov opinions 2016 Kindred Nursing Centers Clark 16-32`
   - `site.ca4.uscourts.gov Noohi Toll Brothers 11-2185 2013 consideration arbitration`
2. An open attempt for the historical Kindred opinion:
   `https://www.supremecourt.gov/opinions/16pdf/16-32_o7jp.pdf`.
3. Search query:
   `Kindred Nursing Centers v Clark 2017 Supreme Court opinion equal treatment`.

None sought Genesis/Ford's own disposition or later history.

## CourtListener MCP

`mcp__courtlistener.search(type="o", citation="708 F.3d 599", court="ca4", num_results=1)`
attempted to verify Noohi's reasoning. It returned HTTP 429, the daily rate
limit, with an approximately 2,211-second wait. No opinion text or search
results were returned. I did not retry or use a direct REST fallback.

## Local contract checks

Read the prediction, tooling, and flags schemas and relevant path and
serialization helper definitions. These supplied output structure only, not
case evidence. Local JSON/model checks and `uv run fedcourts validate data`
are artifact validation, not outcome retrieval.
