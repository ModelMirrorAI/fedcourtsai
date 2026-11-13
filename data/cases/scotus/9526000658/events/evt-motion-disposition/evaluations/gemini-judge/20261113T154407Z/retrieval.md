# Evaluator Retrieval Log (`scotus/9526000658` / `evt-motion-disposition`)

## Corpus CLI (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000658" --event "evt-motion-disposition" --role evaluator`
   - Resolved case, corpus, event, and outcome paths (`no ranged corpus reads`).
2. `uv run fedcourts query --help`
   - Inspected structured filter flags (`no ranged corpus reads`).
3. `uv run fedcourts query --court scotus --docket-number 26A657`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Verified companion application *Paul Schultz v. Kevin McCarthy*, No. 26A657 (`originating_court: "ca4"`, `originating_docket_number: "26-2406"`, `date_decided: "2026-11-10"`), confirming `gemini-baseline`'s forward-mode corpus reference and confirming that `26A657` was also unresolved when `gemini-baseline` ran on `2026-11-09`.

## CourtListener MCP

1. `mcp_courtlistener_read_document(opinion_id=11512446)`
   - Verified the full text of *In re: Paul Schultz*, No. 26-2404 (4th Cir. Oct. 22, 2026) (unpublished *per curiam* before Wilkinson, King, and Rushing, JJ., denying pro se mandamus petition seeking recusal of E.D. Va. District Judge in `1:26-cv-02804-LMB-IDD`).
2. `mcp_courtlistener_analyze_citations(text="Hollingsworth v. Perry, 558 U.S. 183, 190 (2010); Cheney v. United States District Court, 542 U.S. 367, 380 (2004).")`
   - Verified both Supreme Court citations (`558 U.S. 183`, cluster `1747`; `542 U.S. 367`, cluster `136997`).
3. `mcp_courtlistener_read_document(opinion_id=11394602)`
   - Verified the full text of *Paul Schultz v. H. Jason Gold*, Nos. 25-2195 et al. (4th Cir. July 10, 2026) (consolidated unpublished *per curiam* decision affirming E.D. Va. bankruptcy orders and confirming H. Jason Gold's status as Chapter 7 Trustee).

## Web Search

- None.
