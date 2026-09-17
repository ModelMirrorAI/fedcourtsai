# Retrieval record

## Baseline and local context

- Read AGENTS.md, .github/prompts/predict.md, the prediction/flags/tooling schemas, the provisioned event and record inputs. A search for scoped AGENTS.md files under data and .github returned none; no labeling artifacts were opened.
- Ran `uv run fedcourts paths --court scotus --docket 73500230 --event evt-petition-disposition --role predictor`. The default cache was read-only; reran successfully with the cache placed under /tmp. No outcome file was opened.
- Consulted `metrics/statpack.md`: modern-cert disposition and circuit cuts; paid-segment relist and CVSG cuts; sal-v4 prior-Term baseline reached table. Inspected only the top-level keys of `metrics/statpack.json` for metadata. Calculated the denominator-weighted mean of the displayed 2017–2024 baseline reached percentages locally: approximately 0.0512025 over weighted n=11,580.
- No `fedcourts query`, `open-events`, `stats`, or corpus-pull call. No ranged corpus-read transfer lines were produced. No CourtListener MCP call.

## Pre-decision filings beyond the provisioned text

All requests used exact document links from the provisioned snapshot, not a current docket search. No general web search or search for this case's disposition was performed.

### Opposition, filed August 26, 2026

Source: https://www.supremecourt.gov/DocketPDF/25/25-1329/420143/20260826104748541_Cornelia_Bio%20Document%20%20%20August%2026%202026%20EFile.pdf

- One browser open returned no readable content.
- One curl-to-pdftotext attempt failed because pdftotext is not installed; no extracted text resulted.
- Three successful HTTP fetches with in-memory pypdf extraction, 41 PDF pages total. Read PDF pages 4–9, 17–23, 32–33, 36–37, and 40. These include the argument outline and printed argument pages 5–11, 20–21, 24–25, and 28.
- Used the disputed preservation, Rule 56, fee-posture, and public-figure vehicle arguments. The brief also reports another petition's denial, Gopher Media, on June 15, 2026; this is not the target petition's disposition and was weighed with the reply's distinction rather than accepted as a controlling analogue.

### Reply, filed September 11, 2026

Source: https://www.supremecourt.gov/DocketPDF/25/25-1329/423982/20260911171058043_Wealthy%20Reply%20EFILE%20Sep%2011.pdf

- Two browser opens returned no readable content.
- Two successful HTTP fetches with in-memory pypdf extraction, 21 PDF pages total. Read PDF pages 8–17, including printed argument pages 1–9.
- Used the responses to the statute-specific split argument, forfeiture objection, and fee-finality objection, plus the distinction between Gopher Media's immediate-appealability question and this petition's applicability question.

Retrieved PDF bytes were not saved as new input files. No source revealed the target event's outcome. No post-decision history of the target petition was requested.
