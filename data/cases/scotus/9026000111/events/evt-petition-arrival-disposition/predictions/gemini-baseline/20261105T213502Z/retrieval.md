# Retrieval Log: `scotus/9026000111` (`evt-petition-arrival-disposition`)

- **Mode:** `forward` (`decided_before: null`, `cutoff: 2026-07-24`)
- **Predictor:** `gemini-baseline` (`run_id: 20261105T213502Z`)

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. **Query 1 — Look up *Nielsen v. Watanabe*, No. 25-417 (the granted OT2026 *Bivens* merits case referenced as a hold anchor in the petition):**
   - **Command:** `uv run fedcourts query --court scotus --docket-number "25-417"`
   - **Transfer stats:** `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - **Summary of results:** Returned `scotus/73278422` (*Francis Nielsen v. Kekai Watanabe*, No. 25-417, originating from `ca9` No. 23-15605), filed `2025-10-07`, `date_cert_granted: "2026-06-22"`, `disposition: "granted"`, `distribution_count: 4`, `merits_brief_filed: "2026-09-23"`, with D. John Sauer appearing as counsel of record for the United States as amicus curiae.

2. **Query 2 — Retrieve 2020s SCOTUS GVR priors:**
   - **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - **Transfer stats:** `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - **Summary of results:** Returned 10 recent SCOTUS `gvr` dispositions from the 2020s era (including SG-filed GVR in No. 26-48, *Mullin v. National TPS Alliance*, and held petitions GVR'd after merits decisions), confirming how held petitions and SG-related dockets resolve under the `gvr` disposition label.

3. **Query 3 — Retrieve 2020s SCOTUS granted priors:**
   - **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - **Transfer stats:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Summary of results:** Returned 10 recent SCOTUS `granted` dispositions from the 2020s era, including multiple Solicitor General cert petitions granted in OT2026 (e.g., No. 26-104, *Rhoney v. Barbosa da Cunha*; No. 26-204, *Department of Justice v. McNutt*; No. 25-1103, *U.S. DOGE Service v. U.S. District Court*; No. 25-1343, *Blanche v. Ozurumba*).

4. **Query 4 — Attempted lookup of *Egbert v. Boule* by reporter citation:**
   - **Command:** `uv run fedcourts query --court scotus --citation "596 U.S. 482"`
   - **Transfer stats:** `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - **Summary of results:** Returned 0 rows with note that only 200 SCOTUS rows in the local corpus carry parallel reporter citations and advising use of CourtListener MCP for specific citation lookups.

5. **Query 5 — Look up *Goldey v. Fields*, No. 24-809:**
   - **Command:** `uv run fedcourts query --court scotus --docket-number "24-809"`
   - **Transfer stats:** `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - **Summary of results:** Returned `scotus/70670998` (*Howard Goldey, Associate Warden, et al. v. Andrew Fields, III, et al.*, No. 24-809, originating from `ca4` No. 23-6246), `date_cert_granted: "2025-06-30"`, `merits_decided: "2025-06-30"`, `disposition: "granted"`, `merits_judgment: "reversed"`, confirming that a summary reversal at the cert stage is recorded as `disposition: "granted"`.

## 2. CourtListener MCP Queries

1. **`mcp_courtlistener_search` (`type="o"`, `citation="606 U.S. 942"`):**
   - Located *Goldey v. Fields*, 606 U.S. 942 (June 30, 2025) (`cluster_id: 10776815`, `opinion_id: 11243402`).
2. **`mcp_courtlistener_search` (`type="o"`, `citation="115 F.4th 1034"`):**
   - Located *Kekai Watanabe v. Estela Derr*, 115 F.4th 1034 (9th Cir. Sept. 6, 2024) (`cluster_id: 10106380`, `opinion_id: 10572980`), the Ninth Circuit decision under review in *Nielsen v. Watanabe*, No. 25-417.
3. **`mcp_courtlistener_search` (`type="o"`, `citation="145 F.4th 516"`):**
   - Checked for *Orellana v. Godec*, 145 F.4th 516 (4th Cir. 2025); 0 results indexed under that reporter citation string in CourtListener search, but its holding and quotation (`145 F.4th at 525`) are detailed in `petition.txt` (Pet. 13).
4. **`mcp_courtlistener_read_document` (`opinion_id=11243402`):**
   - Read the full text of *Goldey v. Fields*, 606 U.S. 942 (2025) (per curiam), confirming the Court's summary reversal of the Fourth Circuit in a *Bivens* action supported by the United States as amicus curiae.
5. **`mcp_courtlistener_read_document` (`opinion_id=10572980`):**
   - Read the full text of *Watanabe v. Derr*, 115 F.4th 1034 (9th Cir. 2024) (Judge Paez's majority opinion and Judge M. Smith's partial dissent), confirming that the Ninth Circuit's Step-One analysis of factual similarity and refusal to consider alternative administrative remedies at Step One (115 F.4th at 1042–1043) closely parallels the First Circuit majority's Step-One analysis of the Inspector General Act in *Arias v. Herzon*.

## 3. Web Searches

None performed (`used_web_search: false`). No search was conducted for the disposition or subsequent history of *Herzon v. Arias* (No. 26-111).
