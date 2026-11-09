# Retrieval record

## Boundary and local sources

Forward cell. Case-specific materials were limited to the provisioned October 19, 2026 snapshot, event definition, context, document manifest, petition including appendix, questions presented, decision below, lower-court docket extract, and same-question list. No live lookup of this petition, its subsequent history, disposition, or opposition was attempted. No other prediction or evaluation was read.

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`. Read the committed `metrics/statpack.md`, particularly the modern cert, circuit, paid-segment relist/CVSG/amicus, and salience-band sections and the prior-Term reached rates. These local file reads are not remote corpus transfers.

## CLI setup attempts

1. `uv run fedcourts paths --court scotus --docket 9026000355 --event evt-order-call-for-response-disposition --role predictor` failed before executing the CLI because `/home/codexcell/.cache/uv/CACHEDIR.TAG` was not writable. No case data returned.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000355 --event evt-order-call-for-response-disposition --role predictor` succeeded and confirmed case/event paths. The evaluator-only outcome was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` succeeded. Repeated as `UV_CACHE_DIR=/tmp/uv-cache COLUMNS=180 uv run --no-sync fedcourts query --help` for readable filter descriptions. Neither call retrieved case rows.

`--no-sync` used the provisioned environment without installing packages. `UV_CACHE_DIR` only redirected uv's runtime cache to a writable temporary location.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`

   Transfer: `ranged corpus reads: 36 GET(s), 9437184 byte(s)`.

   Returned Goldman Sachs Bank USA v. Brown, No. 25-1408 (four distributions); U.S. DOGE Service v. U.S. District Court, No. 25-1103 (two); and Corey Duran Berry v. United States, No. 25-7026 (five). These are unrelated recent grants, not matched vendor-preemption precedents or a random base-rate sample. They did not determine the grant probability. The term-year filter does not impose an event-date ceiling on these forward-mode results.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '531 U.S. 1058' --citation '572 U.S. 273' --citation '569 U.S. 251' --decided-before 2026 --limit 5`

   Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`.

   No rows returned. The CLI warned that only 200 scoped SCOTUS rows carry reporter citations, that this is an own-citation filter, and that no result likely reflects coverage rather than absence of the authority. No retry through sparse corpus citation filters was made.

## Web calls: general precedent only

1. Batched searches: `site.supremecourt.gov opinions 12pdf Dan's City Used Cars Pelkey 12-52` and `site.supremecourt.gov opinions 13pdf Northwest Ginsberg 12-462`. Returned Cornell reproductions of the opinions, older Supreme Court journal/PDF materials, and irrelevant Petition Clause materials. The relevant Ginsberg result displayed the holding concerning state common-law preemption. No result concerned the target petition's outcome.
2. Batched searches: `"12-462" "supremecourt.gov/opinions/13pdf"` and `"12-52" "supremecourt.gov/opinions/12pdf"`. Returned mostly irrelevant materials; a secondary syllabus page identified the historical Ginsberg decision and linked the slip opinion. No present-case search or outcome result appeared. Secondary commentary did not supply an independent factual premise.
3. Opened `https://www.law.cornell.edu/supremecourt/text/12-52`, the Supreme Court's opinion reproduced by Cornell, decided May 13, 2013: *Dan's City Used Cars, Inc. v. Pelkey*, 569 U.S. 251. Read the distinction between broad relational language and the motor-carrier provision's transportation-of-property limitation. Used only as general preemption context, not a controlling interpretation of the ADA vendor question.

Other primary opinion source surfaced: `https://www.law.cornell.edu/supremecourt/text/12-462`, *Northwest, Inc. v. Ginsberg*, 572 U.S. 273 (2014), considered through search-result text and the provisioned petition's discussion; not separately opened.

## CourtListener MCP

1. `search(type="o", court="scotus", citation="531 U.S. 1058", num_results=3, fields=["caseName", "dateFiled", "citation", "id", "absolute_url", "opinions"])`.

   Returned *Northwest Airlines, Inc. v. Duncan*, decided December 11, 2000, cluster 9259343. Opinion snippets identify certiorari denied (opinion 9254162) and O'Connor dissenting with Rehnquist and Thomas (opinion 9254163), describing the service-definition split. Other matches were unrelated same-page or loose citation matches and were disregarded. The response warned that requested field `id` is not available at the result level; the relevant opinion IDs were included inside `opinions`. No additional pagination or document read was attempted.

## Validation

The cell is checked using `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000355/events/evt-order-call-for-response-disposition/predictions/codex-baseline/20261109T171058Z`. This is local output validation, not retrieval of any outcome.
