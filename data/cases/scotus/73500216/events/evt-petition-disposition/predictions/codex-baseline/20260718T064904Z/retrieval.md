# Retrieval

## Committed base rates

- `metrics/statpack.md` and the 2025 paid-fee detail in `metrics/statpack.json`: modern cert disposition, originating-circuit, relist, CVSG, Term, and fee-class estimates.

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  - Returned no rows and printed no ranged-read line.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  - `ranged corpus reads: 133 GET(s), 34865152 byte(s)`
  - Returned recent granted-petition metadata used only as general context; none concerned this case.

## CourtListener MCP lookups

- Opinion search for `"implied juror bias" "similar crime"`, limited to filings before July 18, 2026. Three results were returned, illustrating the sparse exact-phrase case law.
- Opinion search for `"implied bias" juror victim`, limited to filings before July 18, 2026. The results included *United States v. Jonathan Davis*, 126 F.4th 610 (8th Cir. 2025), one of the recent authorities cited by the petition, and broader state and federal applications of the doctrine.

No web searches were used. I did not retrieve this case's docket, disposition, subsequent history, or decision coverage.
