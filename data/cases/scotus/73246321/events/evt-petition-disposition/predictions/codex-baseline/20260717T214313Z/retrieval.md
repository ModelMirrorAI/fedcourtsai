# Retrieval

- Consulted `metrics/statpack.md` and the Term 2025 paid-fee-class and originating-court details in `metrics/statpack.json` for cert base rates.
- Ran `uv run fedcourts query --court scotus --era 2020s --limit 8` for recent resolved SCOTUS priors. The command reported: `ranged corpus reads: 429 GET(s), 112394240 byte(s)`. The returned set was salience-ranked and was used only as general procedural context, not as a case-matched rate.
- Retrieved and visually inspected the 10-page official Supreme Court petition PDF listed in `record/documents/documents.json`: `https://www.supremecourt.gov/DocketPDF/25/25-1218/405288/20260424145722115_scan_ajimenez_2026-04-24-14-54-11.pdf`. This recovered the questions presented and argument from a provisioned filing whose extracted text was empty.
- No CourtListener MCP lookup or web search was used.
