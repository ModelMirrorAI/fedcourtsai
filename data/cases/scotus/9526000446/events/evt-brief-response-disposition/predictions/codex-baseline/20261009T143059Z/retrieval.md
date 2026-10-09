# Retrieval record

## Local context beyond the provisioned record

- Read the interim-applications section of `metrics/statpack.md` and the corresponding `interim` object in `metrics/statpack.json`. Used only application-Terms 2016–2025 for the disposition baseline: `(17 + 14) / (226 + 75) = 0.10299003322259136`. Same-Term and all-Term figures were not used as the anchor.
- Checked the published pack's provenance with `git log -1 --format='%h %cI' -- metrics/statpack.md`: `3f3ca14f4 2026-10-08T21:56:24Z`. This is a commit date, not the underlying corpus's pull vintage.
- `sha256sum metrics/statpack.md` returned `44a515a4b0927bfc559bf586a73e5f4fb2a71790614e31602c0aa15d69bf572d`.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines. No CourtListener MCP calls. No other predictions, evaluations, outcome files, or topic-label artifacts were read.

## External retrieval

All retrieval occurred October 9, 2026. The case-specific URLs below came from the provisioned snapshot, not a current docket search.

1. A web-tool open of the October 8 opposition PDF returned no readable content:
   `https://www.supremecourt.gov/DocketPDF/26/26A446/428913/20261008134631862_26A446_Wagner_Stay_Opp.pdf`
2. A web-tool open of the general Court rules PDF also returned no readable content and supplied no substantive evidence:
   `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`
3. Attempted `curl -fLsS --max-time 45 <opposition-URL> | pdftotext - -`; `pdftotext` was not installed, so this attempt produced no readable document text.
4. Retrieved the same October 8 opposition using Python `urllib.request.urlopen` and `pypdf.PdfReader` in memory. Six requests displayed PDF pages 1–6, 7–13, 14–17, 18–21, 22–25, and 26–28 respectively. The display of pages 7–13 was partially truncated; the introduction and complete argument/conclusion were available. Citations in `reasoning.md` use the filing's printed page numbers, not PDF indices. The opposition's circuit-split, vehicle, trial-calendar, and equity arguments informed the forecast.
5. Retrieved the October 6 applicant letter in memory using the same Python tools; read both pages:
   `https://www.supremecourt.gov/DocketPDF/26/26A446/428658/20261006152732136_2026-10-06%20Wagner%20SCOTUS%20Letter.pdf`
   Used its reports of the January 12, 2027 trial date and release order in the separate Minnesota prosecution. These developments predate the provisioned cutoff and are not the Supreme Court outcome being forecast.

No web search queries were issued, no subsequent docket state was fetched, and no outcome-revealing material was encountered. Downloaded PDFs were processed in memory, not added to the record or output directory. Administrative reads of the task instructions, schemas, and dependency declaration, path resolution, and artifact validation were not substantive legal retrieval.
