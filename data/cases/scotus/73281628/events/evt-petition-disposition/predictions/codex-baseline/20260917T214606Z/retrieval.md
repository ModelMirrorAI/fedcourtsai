# Retrieval beyond the provisioned inputs

- Read the committed `metrics/statpack.md`, specifically modern cert dispositions, originating-circuit context, paid-segment relist/CVSG cuts, and the `sal-v4` per-Term reached table. Inspected top-level keys in `metrics/statpack.json` for freshness metadata; no dated build stamp was found. Computed the prior-Term weighted anchor locally.
- Web search: `site.supremecourt.gov opinions Azar Garza 17-654 2018 vacatur equity`. The tool returned no usable result content.
- Web open of the known Azar opinion PDF also returned no usable content: `https://www.supremecourt.gov/opinions/17pdf/17-654_5j3b.pdf`.
- CourtListener MCP `search`: type `o`, citation `584 U.S. 726`, one result requested, fields `caseName`, `dateFiled`, `opinions`, `citation`, `absolute_url`. Returned Azar v. Garza, decided June 4, 2018, opinion ID 4280801.
- CourtListener MCP `search_document`: opinion ID 4280801, query `equity`, snippet size 1800. Read the passage explaining the case-specific equitable character of Munsingwear vacatur. No lookup targeted Bell's outcome.
- Retrieved the exact pre-decision reply URL already supplied in the baseline, using Python `urllib.request` and in-memory `pypdf` extraction: `https://www.supremecourt.gov/DocketPDF/25/25-1141/418228/20260805163301044_25-1141--Bell%20Cert%20Reply%20Brief%2008-05%20rtf.pdf`. This is the August 5, 2026 reply, 16 PDF pages; read the substantive reply, printed pages 1–10. Two fetches of the same fixed document were used to read text obscured by terminal output truncation. No downloaded file was written and no docket page was fetched.
- No `fedcourts query` or `open-events` calls were made, so there are no ranged-corpus transfer lines to report.

Operationally, `uv run fedcourts paths --court scotus --docket 73281628 --event evt-petition-disposition --role predictor` initially failed because the default cache was read-only. Repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. Schema and contract reads and validation are operational checks, not case-outcome retrieval.
