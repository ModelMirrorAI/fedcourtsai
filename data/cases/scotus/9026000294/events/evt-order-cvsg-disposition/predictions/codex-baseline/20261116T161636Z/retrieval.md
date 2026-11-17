# Retrieval log

## Provisioned and stable inputs

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the flags and tooling schemas, the event definition, the November 16 snapshot, context, the document manifest and all provisioned document texts, related snapshots 26-292 and 26-293 and their relation manifest, and `same-question.json`. The latter listed no matched petitions. Consulted the modern-cert disposition, circuit, paid-segment relist, CVSG and amicus cuts, and sal-v8 per-Term band table in `metrics/statpack.md`. No other prediction or evaluation directory, outcome file, or topic-labeling artifact was read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000294 --event evt-order-cvsg-disposition --role predictor` failed because the default uv cache was read-only. No retrieval occurred.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000294 --event evt-order-cvsg-disposition --role predictor` succeeded and identified the case and event paths. It explicitly withheld the evaluator-only outcome path.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` and a second help call with `COLUMNS=180` displayed supported structured filters. No priors were retrieved by help.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '573 U.S. 134' --limit 3` returned no matched row. It reported sparse reporter-citation coverage: only 195 SCOTUS rows had any citation. Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --topic sovereign-immunity --limit 5` returned no row and warned that 0 of 592,083 SCOTUS rows carried a topic. Topics are exact circuit nature-of-suit strings, so this was an unhelpful filter, not evidence that comparable cases do not exist. Transfer: `ranged corpus reads: 2314 GET(s), 606142464 byte(s)`.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --limit 3` returned three rows: Robinhood Markets v. Sodha (25-944, cert granted November 13, 2026, following a June 1 CVSG and three distributions); Mullin v. RAICES (26-239, cert granted November 13, 2026); and Mullin v. Friends of the Ruidosa Church (26A560, a substantive interim application granted November 9, 2026). This query deliberately conditions on a grant and mixes cert with substantive applications, so I did not derive an empirical cert probability from it. The Robinhood row is a procedural illustration only, not a legal analogue. Transfer: `ranged corpus reads: 3 GET(s), 786432 byte(s)`.

The uv cache override uses existing installed tooling; no package was installed.

## CourtListener MCP calls

1. `search(type="o", citation="73 F.4th 157", num_results=2)` returned one opinion: *OI European Group BV v. Bolivarian Republic of Venezuela*, Third Circuit, July 7, 2023; cluster 9412117, opinion 9407593. This was a precedent lookup, not a lookup of Owens or its disposition.
2. `search_document(opinion_id=9407593, query="recognition", snippet_size=650)` returned two excerpts, including the withdrawal of recognition of Maduro and recognition of Guaido in the background facts.
3. `search_document(opinion_id=9407593, query="diplomats", snippet_size=2100)` returned the opinion's discussion of Congress assigning FSIA immunity determinations to judges.
4. `search_document(opinion_id=9407593, query="prerogative", snippet_size=2200)` returned the discussion of continuing sovereignty across changes in government, the FSIA's transfer of immunity decisions to courts, and consideration of both rival governments' conduct. Those excerpts informed the limited comparison to the petition's claimed split.

## Web attempts

1. One `web.run` search call used two queries: `site.supremecourt.gov opinions Altmann 541 677 701 executive views immunity` and `site.ca3.uscourts.gov "73 F.4th 157" "recognition"`. The tool returned no usable content or source references. No proposition was adopted from these searches.
2. Two `web.run` open calls attempted the snapshot-linked Faiq amicus PDF, at `https://www.supremecourt.gov/DocketPDF/26/26-294/428540/20261005174238426_Faiq%20cert%20op%20%20-%20final%20to%20printer.pdf`. Both returned no usable content or source references. I did not read or infer the brief's arguments or recommendation.

No search requested this petition's outcome, subsequent history, or anyone else's prediction. No outside forecast or outcome was surfaced by the returned material.
