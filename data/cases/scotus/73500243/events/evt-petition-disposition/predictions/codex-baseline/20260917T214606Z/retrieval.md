# Retrieval record

## Provisioned baseline

Read event.yaml and the case-level record/context.json, record/snapshots/2026-09-17.json, record/documents/documents.json, questions-presented.txt, and selected petition.txt passages, including the questions, posture, principal cert arguments, and conclusion. No outcome file, another prediction, evaluation, or labeling-measurement artifact was consulted.

## Beyond provisioned inputs

1. Read the required instructions and output schemas. Inspected the repository path and serialization helpers for artifact handling.
2. Ran `uv run fedcourts paths --court scotus --docket 73500243 --event evt-petition-disposition --role predictor`. The default cache location was read-only; rerunning with a writable temporary cache succeeded. This resolves paths and is not a corpus-prior lookup.
3. Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid relist/CVSG cuts, and sal-v4 Term table. Read the matching aggregate `metrics/statpack.json` Term segments with jq and pooled elevated prefix rates for 2017–2024: weighted denominator 2,810, weighted grants 484, rate 0.17224199288256228. No individual corpus rows were retrieved. `git log -1 --format='%h %cI' -- metrics/statpack.json` reported `55121cdb8 2026-09-14T11:02:00Z`; this is commit vintage, not corpus freshness.
4. Two web open calls for the exact August 31 opposition URL returned no usable output. A web search for `site.supremecourt.gov "Zorn" "Lalli" 2026` also returned no usable output. That exploratory search used an incorrect caption and informed no legal inference; no case outcome was surfaced.
5. Retrieved the opposition only from the exact filing URL already present in the snapshot:

   `https://www.supremecourt.gov/DocketPDF/25/25-1341/422609/20260831180409169_25-1341%20Brief%20in%20Opposition.pdf`

   An initial curl-to-pdftotext pipeline failed because pdftotext was unavailable. Python urllib plus the installed pypdf then successfully read the 30-page PDF in memory on three requests. Read PDF pages 2–5, 20–22, 24–26, and 28–29 (questions/contents/authority-list excerpt and printed argument pages 13–15, 17–19, 21–22). No retrieved PDF or extracted text was written outside this cell. This document predates the forecast and was selected from the snapshot, not a docket-state or disposition search.

No CourtListener MCP calls, direct CourtListener REST calls, fedcourts query/open-events calls, or corpus-info calls were made. Consequently there are no ranged-corpus transfer lines to report. The reply was not retrieved. Web tools supplied no usable references; the substantive external source was the directly fetched pre-decision opposition, not search results.
