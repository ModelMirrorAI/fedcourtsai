# Retrieval Log

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-459`
   - Transfer: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Purpose: Retrieve the corpus record for *Michael Salazar v. Paramount Global, dba 247Sports* (No. 25-459), the pending OT2026 VPPA case (`case_id: scotus/73278510`, cert granted 2026-01-26) for which Petitioner requests a hold in the alternative.

2. `uv run fedcourts query --court scotus --docket-number 24-994`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Purpose: Retrieve the corpus record for *National Basketball Association v. Michael Salazar* (No. 24-994, `case_id: scotus/72487279`, cert denied 2025-12-08), the Second Circuit VPPA "consumer" precedent (*Salazar II*, 118 F.4th 533) applied in Golden's favor below.

3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Purpose: Retrieve recent 2020s SCOTUS cert priors from the corpus to inspect current-era disposition patterns.

4. `uv run fedcourts query --court scotus --citation "146 S. Ct. 885" --citation "146 S. Ct. 1790"`
   - Transfer: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Purpose: Check whether the SCOTUS certiorari denials in *Solomon v. Flipps Media, Inc.* (146 S. Ct. 885) and *Hughes v. National Football League* (146 S. Ct. 1790) were indexed by reporter citation in the corpus (returned 0 rows with a note that only 200 SCOTUS rows carry reporter citations).

5. `uv run fedcourts query --court scotus --docket-number 26A23`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Purpose: Retrieve the linked extension application (`26A23`, `case_id: scotus/9526000023`) referenced on the docket snapshot for No. 26-398.

## 2. CourtListener MCP Queries

1. `mcp_courtlistener_search` (`type: "o"`, `case_name: "Solomon v. Flipps Media"`) & `mcp_courtlistener_call_endpoint` (`clusters`, `id: 10439012`) & `mcp_courtlistener_read_document` (`opinion_id: 10905600`, chunks 0, 2–8)
   - Purpose: Read the Second Circuit's published decision in *Solomon v. Flipps Media, Inc.*, 136 F.4th 41 (2d Cir. May 1, 2025), which adopted the Third and Ninth Circuits' "ordinary person" standard for "personally identifiable information" under 18 U.S.C. § 2710(a)(3) and served as the binding circuit precedent in *Golden*.

2. `mcp_courtlistener_search` (`type: "o"`, `case_name: "Salazar v. Paramount Global"`) & `mcp_courtlistener_call_endpoint` (`clusters`, `id: 10372262`) & `mcp_courtlistener_read_document` (`opinion_id: 10838850`, chunk 0)
   - Purpose: Read the Sixth Circuit's decision in *Salazar v. Paramount Global*, 133 F.4th 642 (6th Cir. Apr. 3, 2025), to verify that *Salazar* concerns only the threshold "consumer" / "subscriber" definition under 18 U.S.C. § 2710(a)(1) and does not reach the "personally identifiable information" issue under § 2710(a)(3).

3. `mcp_courtlistener_search` (`type: "oa"`, `court: "scotus"`, `case_name: "Salazar v. Paramount Global"`)
   - Purpose: Confirm oral argument date in *Salazar v. Paramount Global*, No. 25-459 (argued October 14, 2026, prior to the October 22, 2026 CFR in No. 26-398).

4. `mcp_courtlistener_search` (queries on `court: "scotus"` for *Solomon v. Flipps Media* and *Hughes v. National Football League* by case name and S. Ct. citation)
   - Purpose: Attempt to locate docket metadata for the prior cert denials in *Solomon* and *Hughes* (confirming the citations and dates already set forth in the provisioned petition).
