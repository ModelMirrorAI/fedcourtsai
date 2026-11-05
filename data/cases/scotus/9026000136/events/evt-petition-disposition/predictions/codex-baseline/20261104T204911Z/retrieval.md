# Retrieval record

## Provisioned inputs

Read the event definition and case-level record: `snapshots/2026-11-04.json`, `context.json`, `same-question.json`, and `documents/documents.json`, `questions-presented.txt`, `petition.txt` (including appendix A), `brief-in-opposition.txt`, and `cert-reply.txt`. No outcome, evaluation, another prediction, or labeling artifact was consulted.

## Repository context and CLI

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json` for the output contract.
- Read `metrics/statpack.md`, particularly modern-cert dispositions, originating circuit, relist counts, CVSG status, and the sal-v6 segment-band reached rates. Used the cell's frozen `cert_anchor` as the primary baseline.
- Searched `docs/cli.md` and the prompt for corpus-query/base-rate instructions. The broad documentation search returned lengthy CLI descriptions; no corpus case query was run.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000136 --event evt-petition-disposition --role predictor`; failed before retrieval because `/home/codexcell/.cache/uv/CACHEDIR.TAG` was not writable.
- Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000136 --event evt-petition-disposition --role predictor`; succeeded, resolving case and event paths without displaying any outcome path. No ranged corpus reads line was printed.

## Web attempts: historical precedents only

The web tool returned no visible content for each of these calls, so none supplied evidence:

1. A two-query search: `site.supremecourt.gov opinions 2019 Thryv Click-to-Call 18-916 mandamus`; `site.supremecourt.gov opinions 2017 SAS Institute Iancu 16-969 statutory limits 314`.
2. A two-query search: `Thryv Inc v Click-to-Call 590 US 45 2020 Supreme Court opinion`; `SAS Institute Inc v Iancu 584 US 357 2018 opinion`.
3. Attempted open of the historical Thryv opinion PDF at `https://www.supremecourt.gov/opinions/19pdf/18-916_new_g3bi.pdf`; no visible content or verification of the guessed filename.

No search concerned Tesla's petition disposition, subsequent history, or coverage of its decision. No current companion-case docket or outcome was retrieved.

## CourtListener MCP

1. `search(type="o", citation="989 F.3d 1375", num_results=2)` returned one match: *Mylan Laboratories Ltd. v. Janssen Pharmaceutica, N.V.*, Federal Circuit, March 12, 2021; cluster 4863478; opinion 4667257. The result's citation-count metadata was not used.
2. `read_document(opinion_id=4667257)` returned the historical Mylan opinion. Used its distinction between mandamus jurisdiction and entitlement to relief, its treatment of statutory challenges to noninstitution, and its Fintiv discussion. This is an older precedent in another case, not this petition's outcome. Conventional citation: 989 F.3d 1375, 1379–83 (Fed. Cir. 2021).

## Validation

Cell validation is run with `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000136/events/evt-petition-disposition/predictions/codex-baseline/20261104T204911Z`. It is an output-integrity check, not case retrieval.
