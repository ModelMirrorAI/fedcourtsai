# Retrieval record

## Local inputs and calculations

Read AGENTS.md, the prediction prompt and schemas, case-level snapshot/context, event definition, document manifest, QP and relevant petition/BIO portions. Consulted committed metrics/statpack.md and matching metrics/statpack.json exact risk-set fields. Computed the OT2017–OT2025 sal-v4 elevated reached anchor as 536/3,139. Read paths/serialization helpers for output construction. No target outcome, other cell output or topic-label artifact was read.

## Corpus and command attempts

- `uv run fedcourts paths --court scotus --docket 9026000004 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help`: both initially failed because the default uv cache was read-only. Repeated each successfully with `UV_CACHE_DIR=/tmp/uv-cache`. Paths explicitly withheld the evaluator-only outcome; help explained structured filters.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era modern --disposition denied --decided-before 2026 --limit 3`: rejected because modern is not a valid decade token. No rows or transfer line. Reissued with 2020s below.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3`: returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. Chicago (25-1098), each denied October 19, 2026. These precede this forecast date; the bare 2026 mask is a docket-Term/year filter, not a calendar-2025 resolution promise. These are not topic-matched priors or a frequency sample. Stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`: failed because the service backend has no client-side connection. No corpus-wide newest-pull/newest-snapshot vintage was obtained. No alternate backend, bulk blob or credentials were sought.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 21-926 --decided-before 2026 --limit 1`: returned Cooper Tire & Rubber Company v. Tyrance McCall, scotus/72475093, denied June 30, 2023, four stored distributions. This corroborates the historical prior discussed in the BIO, not the target petition. Stderr: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`.

## General precedent searches

- Web search: `site.supremecourt.gov opinions 2022 Mallory Norfolk Southern 21-1168 notice registration`. No usable results returned.
- Web search: `Mallory Norfolk Southern 2023 supreme court slip opinion pdf 21-1168`. No usable results returned.
- CourtListener MCP `search(type="o", citation="600 U.S. 122", num_results=2)`: HTTP 429, daily quota exhausted, approximately 2,018 seconds until availability. No opinion returned; no retry or direct REST fallback.

These external attempts concerned the already-decided 2023 Mallory precedent, never this petition's disposition or later history. No target-outcome material surfaced. The forecast relies on the staged record and committed pack, with Cooper Tire's prior denial as limited historical context.

## Output checks

An initial in-memory output-construction attempt failed before writing files because CasePaths was passed an incorrect constructor signature. Corrected to CasePaths(data_root, court_id, docket_id). Output artifacts were created through apply_patch and normalized with fedcourtsai.serialize. A direct JSON Schema check could not start because the optional jsonschema module is not installed; no package was installed. Instead, both JSON artifacts passed their authoritative Pydantic models (Prediction and AgentToolingFeedback). Explicit checks verified all five cert claims, all nine Justice labels, equality of disposition/top-level probabilities, both prose pointers, and exactly six output files. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data` passed after writing: `OK: 29704 artifact(s) valid, 71067 reference(s) consistent`. An earlier concurrently running validator, begun before output creation, also passed its then-visible tree; the post-write result is the relevant one.
