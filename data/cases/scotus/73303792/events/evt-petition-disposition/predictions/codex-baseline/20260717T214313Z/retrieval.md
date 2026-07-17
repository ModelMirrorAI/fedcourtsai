# Retrieval

## CourtListener MCP

- Opinion search for `case_name="John Paul Gomez"`, court `ca6`, filed 2025-01-01 through 2026-07-17: no results.
- Opinion search for `q="\"24-3840\""`, court `ca6`, filed 2025-01-01 through 2026-07-17: no results.
- RECAP search for docket `24-3840`, court `ca6`: found `John Gomez v. David Ryan`, CourtListener docket 69636140.
- RECAP search for `q="\"John Paul Gomez\""`, court `ca6`, filed 2024-01-01 through 2026-07-17: no results.
- Dockets endpoint item 69636140: confirmed the Sixth Circuit docket number and caption; no termination date or substantive metadata was available.
- Docket-entries endpoint schema lookup and recap-documents endpoint schema lookup, used to make a field-limited docket request.
- Docket-entries endpoint for docket 69636140: returned a December 2, 2025 `judge order filed` entry and a February 13, 2025 `ruling letter sent` entry; neither document was available or had text.
- Broad RECAP search for `q="\"John Gomez\" \"David Ryan\""`: produced three irrelevant bankruptcy results.
- Broad RECAP party search for `John Gomez`: produced 422 noisy results and did not identify a useful district-court record.
- Field-limited RECAP search again for docket `24-3840`, court `ca6`: confirmed parties John Gomez and David Ryan and found no attorney metadata.

No CourtListener lookup sought or exposed this petition's disposition.

## Official petition PDF

- Retrieved the 26-page petition from the exact `supremecourt.gov` URL recorded in the provisioned snapshot because the provisioned text layer was empty.
- Rendered all pages locally with PyMuPDF and read the scanned pages. This supplied the questions presented, procedural history, cited authorities, asserted splits, and reasons-for-granting argument. Temporary files were kept under `/tmp`.

## Corpus and base rates

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 8`
  - `ranged corpus reads: 429 GET(s), 112394240 byte(s)`
  - Returned a mixed recent sample of grants and denials. The sample was not closely similar enough to override the structured base rates or the case-specific assessment.
- Consulted `metrics/statpack.md`, especially modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- Consulted the 2025 paid-petition class in `metrics/statpack.json` for the 5.36% estimated grant rate.

No general web search was used.
