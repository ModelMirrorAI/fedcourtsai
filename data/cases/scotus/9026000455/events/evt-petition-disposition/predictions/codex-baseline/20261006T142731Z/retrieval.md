# Retrieval record

## Local materials

- Read the contract and schemas, the assigned event, and the provisioned October 6, 2026 snapshot and context. No provisioned document directory exists.
- Read committed `metrics/statpack.md`: modern discretionary-cert dispositions, originating court, paid-segment relist and CVSG cuts, and sal-v4 prior-Term reached-band rates. Computed the denominator-weighted baseline rate from displayed 2017–2025 rows: approximately 0.050109, weighted n=12,720. This is a committed-pack calculation, not a live corpus query.
- Ran `uv run fedcourts paths --court scotus --docket 9026000455 --event evt-petition-disposition --role predictor`. The first attempt failed on the default cache's read-only location; repeating with a writable temporary cache succeeded. No outcome file was read.
- No `fedcourts query` or `open-events` call was made, and no ranged-corpus transfer line was emitted.

## Exact pre-decision documents

Petition URL, supplied in the baseline:
`https://www.supremecourt.gov/DocketPDF/26/26-455/428497/20261006080338291_20261006-080026-00002458-00006384.pdf`

- Two web `open` attempts returned no content or source handle. No search-results page was obtained.
- A shell HEAD request succeeded (HTTP 200). An attempted curl-to-pdftotext extraction failed because pdftotext was unavailable; curl reported a closed output pipe.
- Retrieved the same URL with Python urllib and extracted its text in memory with pypdf. Three GET/extraction calls covered PDF pages 1–9, 10–20, and a targeted reread of pages 13–16 because a displayed output had been truncated. Read the questions presented, statement, reasons for review, and requested relief. No downloaded file was saved.

Public appendix URL, also supplied in the baseline:
`https://www.supremecourt.gov/DocketPDF/26/26-455/428497/20261006080338668_20261006-080026-00002458-00006385.pdf`

- One urllib GET and in-memory pypdf extraction, both PDF pages. It contains a cover and the February 25, 2026 Eighth Circuit rehearing-denial order. The petition's listed lower-court merits decisions are not present in that public PDF.

## CourtListener MCP

- `search(type="o", court="ca8", docket_number="25-2049", filed_before="2026-04-16", num_results=3)` sought only the pre-petition appellate opinion. The server returned HTTP 429, daily rate limit exceeded, with no opinion results. No REST fallback or token access was attempted.

No current Supreme Court docket, cert disposition, subsequent history, evaluator outcome file, or labeling-measurement artifact was consulted. No general web search was performed. All document retrieval was limited to the two specific pre-decision filings named in the provisioned snapshot.
