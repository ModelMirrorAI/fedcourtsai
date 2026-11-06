# Retrieval record

## Provisioned and repository material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; the specified event definition; the case-level August 18 snapshot, context, document metadata, petition, questions presented, appendix, and same-question file; and `metrics/statpack.md`. No evaluator-only record, other prediction, or topic-label artifact was opened.

## CLI attempts and corpus queries

Commands below ran with the identifiers supplied in the kickoff, not potentially empty shell variables.

1. `uv run fedcourts paths --court scotus --docket 9026000047 --event evt-order-call-for-response-disposition --role predictor` failed before execution because UV's default cache was read-only. Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000047 --event evt-order-call-for-response-disposition --role predictor`; succeeded, resolving the specified event. No outcome path was retrieved.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded and displayed structured filters. No corpus transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era modern --decided-before 2026 --limit 4` was rejected: `modern` is not an era token. No corpus transfer line.
4. Corrected to `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 4`. Succeeded. Stderr: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`. Returned Burford German Funding (25-1269), Roofing Designs (25-1367), Silva Ochoa (25-7569), and Garcia v. Hobbs (25-901), all tagged GVR, with two or three recorded distributions and no opinion bodies. The bare year filters docket-era years rather than restricting resolutions to January 1, 2026; the returned dispositions were dated October 2026. These are unrelated-case context permissible in this forward cell, not this petition's outcome. They supply no estimated success rate and carry little weight.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 21-1572 --decided-before 2026-08-19 --limit 1` succeeded. Stderr: `note: replay cutoff 2026-08-19 (from --decided-before) — priors that had not resolved by then are excluded, on top of any --decided-before Term`; `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned Domino's Pizza, LLC v. Edmond Carmona, corpus case `scotus/72470913`, October 17, 2022 GVR, two distributions, no opinion body. Used as a procedural analogy; its remand basis is also stated in the provisioned appendix.

## Web attempts

1. `web.run` search query: `site.supremecourt.gov "Flowers Foods" "Brock" opinion 2026`. The tool returned no usable result or source identifier.
2. `web.run` open: `https://www.supremecourt.gov/opinions/25pdf/24-935_k53m.pdf`. The tool returned no usable document or source identifier. No facts were taken from these empty responses; the opinion was obtained through MCP instead.

## CourtListener MCP

1. `search(type="o", court="scotus", q='"Flowers Foods" "Brock"', filed_before="2026-08-19", num_results=3)` returned one result: Flowers Foods, Inc. v. Brock, No. 24-935, May 28, 2026, cluster 10865526, opinion 11332974. This is the already-decided precedent, not the petition being forecast.
2. `read_document(opinion_id=11332974)` returned the 29,837-character opinion. Used to check the limited categorical holding and the factual issues expressly left unresolved, especially opinion pp. 7–8.
3. `search(type="o", citation="47 F.4th 428", num_results=1)` returned Lopez v. Cintas, Fifth Circuit No. 21-20089, August 30, 2022, cluster 7861164, opinion 7805030.
4. `search_document(opinion_id=7805030, query="warehouse", snippet_size=1200)` returned six matching excerpts. Used to check the petition's characterization of the claimed circuit conflict, including the categorical warehouse reasoning at 47 F.4th 433.

No live search targeted this petition's disposition, subsequent history, or later docket entries. No direct CourtListener REST request was attempted. Validation is a local schema/completeness check rather than substantive retrieval.
