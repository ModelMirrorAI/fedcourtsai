# Retrieval log

## Local baseline and reference material

Read the prediction prompt and output schemas; the event definition; case-level `record/context.json`; `record/snapshots/2026-10-23.json`; the document manifest, QP text, petition arguments, and relevant bound lower-court decisions. Consulted `metrics/statpack.md`, particularly modern cert dispositions, originating circuit, relist count, CVSG status and prior-Term sal-v8 reached-band rates. Used the context's frozen 0.051587928582714486 cert anchor. No outcome file, other prediction, evaluation, or `data/qp-topics/` material was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000398 --event evt-order-call-for-response-disposition --role predictor` failed before resolving paths because uv attempted to initialize an unwritable cache at `/home/codexcell/.cache/uv`. No remote retrieval occurred and no transfer line was printed.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9026000398 --event evt-order-call-for-response-disposition --role predictor` succeeded. This resolved the case/event paths and labeled the outcome evaluator-only; no outcome was opened. No transfer line.
3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` succeeded and supplied the structured-filter interface. No transfer line.
4. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition granted --era roberts --limit 3` was refused because `roberts` is not a supported decade token. The diagnostic listed valid era values. No corpus rows or transfer line were returned.
5. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-10-23 --limit 3` succeeded. Although this is a forward cell, the extra day restriction kept illustrative priors resolved by the snapshot cutoff. Returned Scanlan v. Coalition for Open Democracy, 26A512 (a substantive application); Association for Education Fairness v. Montgomery County Board of Education, 26-12 (three distributions); and Department of Justice v. McNutt, 26-204 (two distributions). Only the latter two were cert examples; none was treated as a subject-matched or random sample. No opinion bodies were requested.

   Transfer line, verbatim: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`.

The query also printed: `note: replay cutoff 2026-10-23 (from --decided-before) — priors that had not resolved by then are excluded, on top of any --decided-before Term`. That label reflects the voluntarily supplied retrieval filter, not a change to this cell's forward mode.

## Web calls

1. Searched `site.supremecourt.gov "25-459" "Salazar"`. Results included the official docket, filed briefs, and argument transcript. A nonofficial forecast preview also appeared despite the domain term; I did not open or rely on it. No search mentioned Golden, NBCUniversal, 26-398, or this petition's disposition.
2. Opened the official Salazar docket: `https://www.supremecourt.gov/search.aspx?filename=%2Fdocket%2Fdocketfiles%2Fhtml%2Fpublic%2F25-459.html`. Confirmed cert granted January 16, 2026, and argument October 6, 2026. These predate the October 23 baseline. The returned page also displayed an October 29 corporate letter entry in that other case; it was disregarded. No Golden docket was retrieved.
3. Opened that same Salazar docket again; it returned the same official record. Used only the pre-cutoff grant, question-presented link and argument date, not subsequent entries or argument content.
4. Opened the official granted-question sheet: `https://www.supremecourt.gov/qp/25-00459qp.pdf`. It specifies whether the VPPA's consumer definition covers a subscriber to any goods/services from a provider, or only audiovisual goods/services. This confirmed that Salazar's issue differs from Golden's PII issue. The one-page sheet records the January 16, 2026 grant. No decision or argument transcript was retrieved.

## CourtListener MCP calls

1. `search(type="o", citation="820 F.3d 482", num_results=2)` returned one match, *Yershov v. Gannett Satellite Information Network, Inc.*, First Circuit, April 29, 2016; cluster 3199367, opinion 3199261.
2. `read_document(opinion_id=3199261)` returned the original appellate opinion text (31,055 characters; the tool display was abbreviated). Its facts involve GPS coordinates, Android identifiers, viewing information and Adobe's ability to identify a user. No Supreme Court docket or subsequent history of Golden was requested.
3. `search_document(opinion_id=3199261, query="foreseeably", snippet_size=1100)` returned two excerpts. They confirm the recipient-linkage analysis at page 486 and the fact-specific pleading-stage limitation at pages 489–490. Used to assess the petition's split claim without simply accepting all its characterizations.

Primary opinion source: `https://www.courtlistener.com/opinion/3199367/yershov-v-gannett-satellite-information-network-inc/`.

## Validation

Command: `UV_NO_CACHE=1 UV_NO_SYNC=1 uv run fedcourts validate data --cell data/cases/scotus/9026000398/events/evt-order-call-for-response-disposition/predictions/codex-baseline/20261109T212928Z`.

Result: `OK: 30153 artifact(s) valid, 71728 reference(s) consistent; cell complete`. Repeated the same command after recording this result. Cache and synchronization are disabled to respect the fixed-tooling/no-install contract. This is local output validation, not outcome retrieval.
