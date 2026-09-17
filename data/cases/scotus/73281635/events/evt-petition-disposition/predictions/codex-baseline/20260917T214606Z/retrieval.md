# Retrieval record

## Local inputs and reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling JSON schemas; checked for scoped instructions.
- Read this cell's event definition, `record/context.json`, `record/snapshots/2026-09-17.json`, and `record/documents/documents.json`; read the QP and substantive petition/BIO excerpts, including the appellate opinion in the petition appendix. No other predictor's output or realized outcome was read.
- Read `metrics/statpack.md`: modern-cert disposition, paid-segment relist/CVSG cuts, and the sal-v4 per-Term band table. Inspected top-level keys of `metrics/statpack.json`; no case-level measurement artifact was consulted. Computed the pooled prior-Term elevated reached rate using jq.
- Ran `uv run fedcourts paths --court scotus --docket 73281635 --event evt-petition-disposition --role predictor`; the default cache failed read-only. The same command succeeded with `UV_CACHE_DIR=/tmp/uv-cache`.
- No `fedcourts query` or `open-events` lookup was made, and no ranged-corpus transfer line was emitted.

## Web searches

One web tool call contained two general-precedent searches: `"White v. Chafin" "1068" prejudgment interest` and `"Poleto" "1278" "dicta" prejudgment interest`. The tool returned no usable result text. Neither query sought this petition's outcome, and neither supplied evidence used in the forecast.

## CourtListener MCP

1. `search(type="o", citation="862 F.3d 1065", num_results=2)` returned the July 10, 2017 White opinion, indexed as White v. Wycoff, with the full caption identifying Chafin as defendant-appellee; opinion ID 4184847.
2. `read_document(opinion_id=4184847)` supplied the White opinion. Used its discretionary-interest framework, not metadata about later citations.
3. `search(type="o", citation="81 F.3d 844", num_results=1)` was an erroneous citation lookup while locating the Fourth Circuit authority. It returned an unrelated 2012 district-court jury-demand case; disregarded. I corrected the lookup from the provisioned petition's actual citation rather than relying on this result.
4. `search(type="o", case_name="Gilliam v. Allen", court="ca4", num_results=1)` returned the March 8, 2023 Fourth Circuit decision, 62 F.4th 829, opinion ID 9378265.
5. `search_document(opinion_id=9378265, query="fully compensate", snippet_size=1900)` supplied the relevant passage on jury compensation, discretion, and double recovery. Used to assess whether the claimed categorical conflict is clean.

All live legal retrieval concerned earlier precedent, not this petition's own disposition or subsequent history. No outcome-revealing material for this petition surfaced.
