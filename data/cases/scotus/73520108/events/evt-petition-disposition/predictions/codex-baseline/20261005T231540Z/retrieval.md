# Retrieval record

## Provisioned materials

Read the event, record/context.json, record/snapshots/2026-10-05.json, record/documents/documents.json, questions-presented.txt, and selected pertinent portions of petition.txt and brief-in-opposition.txt. These are the common inputs, not external retrieval.

## Committed aggregate context

Read metrics/statpack.md's modern-cert, originating-circuit, paid relist, paid CVSG, and sal-v4 reached-band sections. Read matching fields in metrics/statpack.json and calculated the prior-Term elevated pool with a local Python command: 484 grant-family equivalents / 2,810 weighted resolved petitions, Terms 2017-2024. No case-level corpus query or open-events call was made, so there is no ranged corpus reads transfer line to report. No CourtListener MCP call was made.

## Targeted retrieval of pre-decision filings

Only URLs already present in the provisioned snapshot were opened. No search for this case's outcome or subsequent history was performed.

1. Attempted web.open on the respondents' September 14, 2026 supplemental brief. The tool returned no content. The exact requested URL was:

       https://www.supremecourt.gov/DocketPDF/25/25-1408/424031/20260914102935061_Goldman%20v.%20Brown%20supplemental%20brief.pdf

2. Attempted curl piped to pdftotext for the petitioner's September 15, 2026 supplemental response. pdftotext was unavailable; the pipeline returned no extracted text and curl reported a broken output pipe. The requested URL was:

       https://www.supremecourt.gov/DocketPDF/25/25-1408/424247/20260915113025469_2026-09-15%20SCT%2025-1408%20Goldman%20Sachs%20Bank%20Suppl%20Br.pdf

3. Retrieved both URLs with Python urllib.request and extracted their PDFs in memory with the installed pypdf. The first combined output contained font warnings and was truncated. I repeated the respondents' extraction for all non-cover pages with font warnings suppressed, then repeated the petitioner's first substantive page; the initial extraction had exposed its remaining substantive pages. No downloaded files were persisted. Respondents' pp. 1-2 and petitioner's pp. 1-4 describe the September 10 bankruptcy-court dismissal without prejudice and debate its effect on certworthiness. Neither reveals this Supreme Court petition's disposition. Those filings materially informed the vehicle adjustment.

## Operational commands

Ran fedcourts paths for this court, docket, event and predictor role. Its first invocation failed because the default package-manager cache was read-only; rerunning with a writable temporary cache succeeded. Read the output schemas and repository path/serialization helpers to conform the artifacts to the contract. Validation is operational, not outcome retrieval. No forbidden outcome files or QP-label artifacts were opened.
