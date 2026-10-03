# Retrieval record

## Local reference material

- Read the task contract and prediction, flags, and tooling schemas.
- Read the committed `metrics/statpack.md`: modern-cert disposition and circuit cuts, paid-segment relist/CVSG cuts, and sal-v4 reached-band table. Used only Terms 2017–2024 for the Term-2025 state-band anchor.
- Read matching `metrics/statpack.json` state segment fields to compute the unrounded prior: sum of `prefix_est_grant_rate * prefix_weighted_resolved` divided by summed `prefix_weighted_resolved`, yielding 89/392.
- Ran `uv run fedcourts paths --court scotus --docket 73500226 --event evt-petition-disposition --role predictor`. The first attempt failed because the default cache was read-only; retrying with a writable temporary cache succeeded. This is path resolution, not a corpus lookup.
- No `fedcourts query`, `open-events`, or CourtListener MCP calls. No ranged-corpus transfer lines were produced. No own-case outcome or other predictor's output was read.

## Fixed pre-decision filings

All URLs were taken from the provisioned snapshot, not discovered by searching the case's outcome. The cell is forward-mode with no retrieval cutoff. Each filing predates the October 3 snapshot.

1. Authority respondents' response, filed August 28, 2026:

   `https://www.supremecourt.gov/DocketPDF/25/25-1325/422375/20260828135252932_No.%2025-1325_Response_of_The_Horseracing_Integrity_and_Safety_Authority_Respondents.pdf`

   One web-tool open returned no usable content. One subsequent direct official-site GET through Python's standard HTTP client succeeded; extracted the 31-page PDF in memory with pypdf. The terminal display was truncated; relied particularly on the displayed rulemaking and vehicle discussion at printed pages 19–23. The response recommends a companion hold and, if this case is granted, limiting review to enforcement.

2. Federal respondents' brief, filed August 28, 2026:

   `https://www.supremecourt.gov/DocketPDF/25/25-1325/422408/20260828160521658_25-1325%20Oklahoma%20CertResponse.pdf`

   One web-tool open returned no usable content. A `curl -I --max-time 20` request to that fixed URL returned HTTP 200. Two direct GETs and in-memory pypdf extraction followed: first the 19-page document, whose terminal display was truncated but included the conclusion and printed pages 12–14; then printed pages 6–10 specifically to read the facial-challenge and supervision arguments. The brief acknowledges a renewed enforcement split, opposes review of rulemaking, and recommends holding this petition for Nos. 26-199 and 26-201.

3. Petitioners' reply, filed September 15, 2026:

   `https://www.supremecourt.gov/DocketPDF/25/25-1325/424246/20260915112450507_HISA%20-%20Cert%20Reply.pdf`

   Two direct GETs with in-memory pypdf extraction of the 14-page document, reading physical pages 5–9 and 10–14. This covered the substantive reply at printed pages 1–7. It urges a grant here or consolidation, identifying a potential appellate-finality problem in the Fifth Circuit vehicle and defending the broader rulemaking question.

No web searches were run. No current docket pages, post-filing case updates, merits outcomes, or disposition coverage were requested. No fetched documents were written into the provisioned record or any other directory.
