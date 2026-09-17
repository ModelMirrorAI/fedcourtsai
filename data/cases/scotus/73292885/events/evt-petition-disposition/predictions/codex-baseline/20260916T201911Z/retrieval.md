# Retrieval log

## Local inputs and aggregate context

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas.
- Read the event definition, `record/context.json`, `record/snapshots/2026-09-16.json`, `record/documents/documents.json`, `questions-presented.txt`, and selected petition sections. Inspected the provisioned opposition text size; its text is unavailable as the metadata reports.
- Read the committed `metrics/statpack.md` modern-cert, paid relist, paid CVSG, and sal-v4 Term-band sections, plus corresponding `metrics/statpack.json` fields. Used jq to pool reached-baseline rates for all displayed strictly-prior Terms, 2017–2024. No fresh corpus query was used.
- Path resolution: `uv run fedcourts paths --court scotus --docket 73292885 --event evt-petition-disposition --role predictor`. The first invocation failed because the default uv cache directory was read-only. Repeated successfully with the cache directed to `/tmp/uv-cache`.
- No `fedcourts query` or `open-events` call; no ranged-corpus transfer line was produced. No outcome artifact or labeling-measurement artifact was read.

## Web attempts

The following four web tool calls returned no usable rendered response in this session. No factual assertion in the forecast depends on content supposedly obtained from them.

1. Search queries: `site.supremecourt.gov opinions 2023 Rahimi 22-915 due process` and `site.supremecourt.gov rules Rule 10 certiorari rarely granted erroneous factual findings`.
2. Open the specific pre-decision opposition PDF already identified in provisioned metadata: `https://www.supremecourt.gov/DocketPDF/25/25-1249/413881/20260623162345311_25-1249%20BIO%20Main%20Document.pdf`.
3. Search queries: `site.law.cornell.edu 18 USC 2265 notice opportunity heard` and `site.supremecourt.gov Rule 10 certiorari erroneous factual findings`.
4. Open the statutory text at `https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title18-section2265`.

## CourtListener MCP

1. `search(type="o", case_name="United States v. Rahimi", court="scotus", filed_after="2024-06-20", filed_before="2024-06-23", num_results=3)`. Returned three versions of the June 21, 2024 decision, citation 602 U.S. 680. Selected revised slip opinion 10290956, not any subsequent litigation.
2. `search_document(opinion_id=10290956, query="due process", snippet_size=900)`. Returned five excerpts. Relied on the majority's concluding holding and footnote 2 at slip-opinion page 17: the limited credible-threat holding and the express reservation of due-process questions. Other excerpts included separate writings; they were not treated as majority holdings.

This was general legal-context retrieval about a different, earlier case. No retrieval sought the target petition's disposition or subsequent history.
