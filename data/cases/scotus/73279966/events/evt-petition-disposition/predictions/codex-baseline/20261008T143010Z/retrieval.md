# Retrieval record

## Local inputs and base rates

- Read the repository instructions, prediction prompt, prediction/tooling schemas, this cell's event definition, `record/context.json`, `record/snapshots/2026-10-07.json`, and the provisioned document manifest, QP, petition argument excerpts, and opposition argument excerpts.
- Read relevant modern-cert, paid-segment relist/CVSG, and sal-v4 per-Term sections of `metrics/statpack.md`. Inspected only the top-level keys of `metrics/statpack.json` when looking for freshness metadata. Calculated the approximate denominator-weighted high-band reached anchor from the markdown table for Terms 2017–2024.
- Path command: `uv run fedcourts paths --court scotus --docket 73279966 --event evt-petition-disposition --role predictor`. Initial execution failed because the default uv cache was read-only; retry with a writable temporary cache succeeded. This was path resolution, not a corpus lookup.
- No `fedcourts query`, `open-events`, live corpus lookup, or CourtListener MCP lookup. No ranged-corpus transfer line was emitted.

## Targeted external retrieval

All three sources were filed before the October 7 snapshot and linked in that snapshot. I did not search for the case's disposition or open its live docket.

1. United States amicus brief, filed September 15, 2026:
   `https://www.supremecourt.gov/DocketPDF/25/25-828/424228/20260915105245693_25-828cvsg_GEO_Nwauzor_final.pdf`
   Two `web.run` direct-open attempts returned no usable content. A subsequent `curl` pipe failed because `pdftotext` was unavailable. Retrieved successfully using `httpx` and parsed in memory with installed `pypdf`, HTTP 200, 29 PDF pages. First successful fetch displayed PDF pages 6, 14, and 29, containing the recommendation, discussion opening, and conclusion; a second fetch displayed pages 15 and 25–28 for the substantive review arguments. No downloaded copy was written to the repository.
2. Washington supplemental brief, filed September 29, 2026:
   `https://www.supremecourt.gov/DocketPDF/25/25-828/425985/20260929160222360_StateSupplBr.pdf`
   Retrieved with `httpx` and parsed in memory with `pypdf`, HTTP 200, 17 PDF pages. First fetch displayed pages 2–4 and 17; second fetch displayed pages 5–8 and 16. Consulted its opening and review arguments, including its treatment of Hencely and comparator facilities. Some terminal output was truncated; I do not claim full-document review.
3. Nwauzor supplemental brief, filed September 29, 2026:
   `https://www.supremecourt.gov/DocketPDF/25/25-828/425966/20260929142637616_2026.09.28%20Nwauzor%20Supplemental%20Brief.pdf`
   Retrieved with `httpx` and parsed in memory with `pypdf`, HTTP 200, 7 PDF pages. First fetch displayed pages 2–4 and 6; second fetch displayed page 5. Consulted the substantive argument on changed detention standards, comparator facilities, and opposition to certiorari.

No web search was conducted. No outcome-revealing material was encountered. The standards and precedent discussed in the supplemental filings were considered as the parties' arguments, not independently retrieved or verified authorities.
