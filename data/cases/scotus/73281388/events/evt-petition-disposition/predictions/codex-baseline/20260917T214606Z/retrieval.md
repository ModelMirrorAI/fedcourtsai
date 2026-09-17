# Retrieval record

All case-specific retrieval was confined to pre-disposition filings or the lower-court opinion, using exact PDF locations supplied by the snapshot. No current Supreme Court docket, petition outcome, subsequent history, or outcome coverage was requested.

## Committed context

- Read `metrics/statpack.md`: modern-cert disposition and circuit tables, paid-segment relist/CVSG cuts, and the sal-v4 per-Term reached-band table.
- Read selected fields of `metrics/statpack.json` to calculate the 2017–2024 elevated risk-set anchor: 484 / 2,810 = 0.17224199288256228.
- No `fedcourts query` or `open-events` invocation; no ranged-corpus transfer lines were generated.

## Official filings and opinion

1. Attempted `web.open` for the July 20, 2026 reply at the URL below. The tool returned no usable content. No web search was performed.
2. Attempted `curl` of the September 9 supplement piped to `pdftotext`; extraction failed because `pdftotext` was not installed. The pipe failure yielded no text.
3. Fetched the supplement with `httpx` and extracted its five PDF pages in memory with `pypdf`; HTTP 200. Read the entire brief. Source: petitioner's supplemental brief, September 9, 2026, printed pages 1–4.

   `https://www.supremecourt.gov/DocketPDF/25/25-1105/423591/20260909155307313_Thompson%20Supp%20Brief%20Final%20pdfa.pdf`

4. Fetched the 18-page reply with `httpx`/`pypdf`; HTTP 200. Selected pages containing preservation/waiver terms, then fetched again to read PDF pages 15–17, corresponding to printed pages 11–13. Also read PDF pages 6 and 14 from the initial term selection. Source: petitioner's reply, July 20, 2026.

   `https://www.supremecourt.gov/DocketPDF/25/25-1105/416882/20260720141830581_Thompson%20Reply%20FINAL%20PDFA%207-20-26.pdf`

5. CourtListener MCP `search`: `type="o", citation="159 F.4th 91", court="ca1", num_results=3`, requesting case name, date, citation, opinions, and URL. Returned zero results; query identifier `176ac79f`. This was a lookup of the lower-court opinion, not this petition's disposition. No CourtListener REST fallback was used.
6. Fetched the First Circuit opinion from the snapshot's official PDF link with `httpx`/`pypdf`; HTTP 200, 35 pages. First searched for selected doctrinal phrases, then fetched again and normalized whitespace to locate the criminal-tracking comparison and footnote 18 on PDF page 33. Also viewed the retrieved background passages on PDF pages 10 and 25. Source: First Circuit opinion dated November 18, 2025, appeal 25-1007.

   `https://www.supremecourt.gov/DocketPDF/25/25-1105/387415/20251215132807378_2025.11.18%20-%20Thompson%201st%20Cir%20Opinion%2025-1007%20PDFA.pdf`

Richards v. Newsom was encountered only through the pre-decision supplemental brief; its opinion was not independently retrieved. No outcome-revealing material was encountered.

## Local tooling

Read the task/schema contracts and the relevant path and serialization helpers. `fedcourts paths` initially failed because the default uv cache was read-only; rerunning with a writable temporary cache succeeded. JSON model checks and `fedcourts validate data` are local validation, not substantive retrieval.
