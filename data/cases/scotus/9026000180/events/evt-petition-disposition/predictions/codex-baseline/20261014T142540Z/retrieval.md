# Retrieval log

## Provisioned materials

Read event.yaml; record/context.json; record/snapshots/2026-10-14.json; record/documents/documents.json; questions-presented.txt; and selected portions of petition.txt, including the substantive arguments, vehicle discussion, and appended Ninth Circuit memorandum. The appendix is truncated as disclosed by the manifest. No outcome file, other prediction, or labeling-measurement artifact was read.

## Beyond provisioned inputs

- Read the output-contract schemas and predict prompt as task instructions.
- Read committed metrics/statpack.md: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Read the matching metrics/statpack.json Term/segment fields and computed the baseline reached pool for the displayed prior-Term window, 2017-2025: 643 / 12,877 = 0.04993399083637493. No remote corpus was queried, so no ranged-corpus transfer line exists.
- Web search call 1: `site.supremecourt.gov opinions Taylor Riojas 2020 qualified immunity obvious`; `site.supremecourt.gov Baxter Bracey 2020 Thomas qualified immunity history`. The tool returned no usable result content.
- Web search call 2: `Taylor v Riojas 141 S Ct 52 Supreme Court 2020`. The tool again returned no usable result content. No factual proposition was drawn from either empty response.
- CourtListener MCP `search(type="o", citation="141 S. Ct. 52", num_results=2)`, query ID `01e42911`: returned an incidental Sanchez v. Mayorkas result and the intended Taylor v. Riojas result. Only Taylor was used; no further results were requested.
- CourtListener MCP `read_document(opinion_id=4582848)`: read Taylor v. Riojas, 592 U.S. 7, 141 S. Ct. 52, decided November 2, 2020, including the per curiam qualified-immunity analysis and separate writing. This is general pre-existing precedent, not this cell's case or subsequent history.

## Local commands

`uv run fedcourts paths --court scotus --docket 9026000180 --event evt-petition-disposition --role predictor` initially failed because the default uv cache directory was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`. This command resolves local paths only. No `fedcourts query`, `open-events`, corpus mutation, or direct CourtListener REST request was made.
