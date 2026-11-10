# Retrieval log

## Provisioned inputs and local context

Read `.github/prompts/predict.md`, the prediction/flags/tooling schemas, this event's `event.yaml`, `record/context.json`, `record/snapshots/2026-11-09.json`, and `record/documents/{documents.json,questions-presented.txt,petition.txt,party-letter.txt}`. Consulted `metrics/statpack.md`, especially the paid-segment relist, CVSG, amicus, and `sal-v8` reached-band sections. No other cell's predictions, evaluations, realized outcome, or QP-topic artifacts were read.

## CLI setup and failed attempts

1. `uv run fedcourts paths --court scotus --docket 9026000396 --event evt-petition-disposition --role predictor` failed before execution because `/home/codexcell/.cache/uv` was read-only. No corpus transfer line.
2. `uv run fedcourts query --help` failed for the same cache reason. No query executed and no transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000396 --event evt-petition-disposition --role predictor` succeeded, identifying the event and corpus paths while keeping the outcome path evaluator-only.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` succeeded; read structured-filter usage. No corpus query or transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 3` failed because `modern` is not a permitted decade token. The error supplied the valid vocabulary; no transfer line.

## Corpus lookups

6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`

   `ranged corpus reads: 5 GET(s), 1310720 byte(s)`

   Returned Jesenik, No. 25-7515; MacRitchie, No. 25-7522; and Waidla, No. 25-7555. All returned denial dates were November 9, 2026; the Term-based filter is not a strict calendar-day exclusion. These unrelated priors supplied no topic-specific inference and were not used to estimate this case's grant probability. This is a forward cell, and none is the target petition.

7. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 25-818 --limit 1`

   `ranged corpus reads: 18 GET(s), 4718592 byte(s)`

   Returned *Terrell Anthony Hargrove v. Ian Healy, Warden*, confirming April 20, 2026 denial, one distribution, and no CVSG. This comparator and its earlier disposition were already identified in the provisioned petition. No opinion body or BIO was returned.

8. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --docket-number 25-5930 --limit 1`

   `ranged corpus reads: 1 GET(s), 262144 byte(s)`

   Returned *William Maxwell v. Sandra Dinis, Acting Warden*: cert granted June 1, 2026, three distributions, no recorded merits judgment. Used only as related habeas litigation identified by the petition, not as a same-question lead case or an outcome of the target petition.

## CourtListener MCP

9. `mcp__courtlistener.search(type="o", citation="151 F.4th 1076", num_results=3)` returned zero matches, query ID `531199dd`. No opinion was retrieved. The provisioned appendix and petition remain the sources for the asserted split. No direct REST workaround was attempted.

## Web attempts

10. One `web.run` call submitted two searches: `"Gonzalez v. Herrera" "151" "1076" supervised release` and `"Hargrove v. Healy" "155" "530"`. The tool returned no usable result content or source references. Neither search requested this petition's disposition.
11. One `web.run` open attempted the exact October 9 predecision party-letter PDF identified in the snapshot:

    `https://www.supremecourt.gov/DocketPDF/26/26-396/429157/20261009163213553_Rivera-Perez%20Letter%20FINAL.pdf`

    The tool returned no usable content or source reference. No substantive text was recovered and no outcome material surfaced. No live target-docket or target-disposition search was performed.

## Validation

Used the contract's cell validator with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000396/events/evt-petition-disposition/predictions/codex-baseline/20261109T212928Z`. This is a local output-contract check, not a source of case evidence.
