# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --stage merits --exclude-case scotus/73500212 --decided-before 2026-11-14 --topic "civil contempt injunction fair ground of doubt Taggart" --limit 15 --log-to /home/runner/.gemini/tmp/fedcourtsai/retrievals.jsonl`
   - **Result:** Rejected by CLI parser (`Exit Code: 2`, `No such option: --stage`); no corpus reads executed.

2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2025 --limit 15 --log-to /home/runner/.gemini/tmp/fedcourtsai/retrievals.jsonl`
   - **Result:** Rejected by CLI parser (`Exit Code: 2`, `No such option: --log-to`); no corpus reads executed.

3. `uv run fedcourts query --court scotus --disposition granted-in-part --era 2020s --decided-before 2025 --limit 10`
   - **Stderr:** `ranged corpus reads: 1144 GET(s), 299761664 byte(s)`
   - **Result:** 0 rows returned (certiorari grants limited to one question are stored under `disposition: "granted"` rather than `"granted-in-part"`).

4. `uv run fedcourts query --court scotus --docket-number 18-489 --decided-before 2025 --limit 5`
   - **Stderr:** `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   - **Result:** 1 row returned — `scotus/15006766`, *Bradley Weston Taggart v. Shelley A. Lorenzen, Executor of the Estate of Stuart Brown, et al.*, 587 U.S. 554 (2019), `originating_court: "ca9"`, `disposition: "granted"`, `merits_judgment: "vacated"`, `merits_decided: "2019-06-03"`.

5. `uv run fedcourts query --court scotus --docket-number 23-344 --decided-before 2025 --limit 3`
   - **Stderr:** `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - **Result:** 1 row returned — `scotus/72479905`, *Apple Inc. v. Epic Games, Inc.* (prior cert-stage docket from underlying liability/injunction appeal), `disposition: "denied"`, `date_cert_denied: "2024-01-16"`.

6. `uv run fedcourts query --court scotus --docket-number 23-367 --decided-before 2025 --limit 3`
   - **Stderr:** `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - **Result:** 1 row returned — `scotus/68462680`, *Starbucks Corporation v. M. Kathleen McKinney*, `disposition: "granted"`, `merits_judgment: "vacated"`, `merits_decided: "2024-06-13"`.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="587 U.S. 554", filed_before="2026-11-14")`
   - **Result:** 1 hit — *Taggart v. Lorenzen*, 587 U.S. 554 (2019) (`cluster_id: 4625564`, `opinion_id: 4402817`, `docketNumber: "18-489"`, unanimous opinion by Breyer, J., filed `2019-06-03`).

2. `mcp_courtlistener_search(type="o", court="scotus", q='"Taggart v. Lorenzen" OR "fair ground of doubt"', filed_before="2026-11-14", num_results=10)`
   - **Result:** 27 hits total (10 returned), including *Taggart v. Lorenzen* and prior Supreme Court contempt/equity decisions citing the "fair ground of doubt" standard (*California Artificial Stone Paving Co. v. Molitor*, 113 U.S. 609 (1885), etc.).

3. `mcp_courtlistener_read_document(opinion_id=4402817)`
   - **Result:** Full opinion text (`40,908` characters) of *Taggart v. Lorenzen*, 587 U.S. 554 (2019), confirming unanimous 9–0 vacatur and remand of the Ninth Circuit's civil-contempt standard.

4. `mcp_courtlistener_search(type="o", citation="144 S. Ct. 681", filed_before="2026-11-14")`
   - **Result:** 2 older unrelated substring matches (*Corso v. Security-First National Bank*, 362 U.S. 144 (1960); *The Servia*, 149 U.S. 144 (1893)); the January 2024 cert denial in *Apple Inc. v. Epic Games, Inc.* was not indexed under that citation query.

## Web Searches

None attempted.
