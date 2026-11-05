# Retrieval Log — `scotus/9026000379` (`evt-petition-arrival-disposition`)

- **Mode:** `forward` (`decided_before: null`, unrestricted retrieval)
- **Predictor / Run:** `gemini-baseline` / `20261105T203825Z`

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - **Transfer:** `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - **Purpose & Findings:** Retrieved recent OT2026 granted SCOTUS petitions, including *Philip L. Rhoney v. Ricardo Aparecido Barbosa da Cunha*, No. 26-104 (granted Oct. 1, 2026, from the Second Circuit, involving 8 U.S.C. § 1225(b)(2)(A) vs. § 1226(a) immigration detention), and other Solicitor General grants (*Department of Justice v. McNutt*, No. 26-204; *Blanche v. Ozurumba*, No. 25-1343; *U.S. DOGE Service v. U.S. District Court*, No. 25-1103).

2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - **Transfer:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Purpose & Findings:** Checked recent OT2026 GVR dispositions for comparison.

3. `uv run fedcourts query --court scotus --docket-number 25-886`
   - **Transfer:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Purpose & Findings:** Retrieved the predecessor case *Kenneth Genalo, Director of the New York Field Office of U.S. Immigration and Customs Enforcement, et al. v. Carol Williams Black, et al.*, No. 25-886 (`scotus/73280386`), confirming that certiorari was granted on `2026-06-15`, merits brief was filed on `2026-08-31`, and merits terminated via `voluntary-dismissal` after mootness.

4. `uv run fedcourts query --court scotus --docket-number 26-104`
   - **Transfer:** `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - **Purpose & Findings:** Confirmed metadata for *Rhoney v. Barbosa da Cunha* (`scotus/9026000104`), originating from the Second Circuit (`25-3141`).

5. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 20` and `uv run fedcourts query --court scotus --era 2020s --include-open --limit 50`
   - **Transfer:** `ranged corpus reads: 0 GET(s), 0 byte(s)` (both calls)
   - **Purpose & Findings:** Checked recent open and resolved OT2026 dockets involving Solicitor General D. John Sauer.

## 2. CourtListener MCP Retrieval

1. **Second Circuit Docket (`C. v. Noem`, No. 26-1396, `docket_id: 73412762`):**
   - Located via `mcp_courtlistener_search` (`type="r"`, `court="ca2"`, `docket_number="26-1396"`), `mcp_courtlistener_get_endpoint_item` (`endpoint_id="dockets"`, `item_id=73412762`), and `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=73412762`).
   - Confirmed appeal was filed `2026-05-20` from S.D.N.Y. (`1:26-cv-01833`, Judge Paul A. Engelmayer's Opinion & Order of `2026-03-20`). Confirmed the government moved for summary affirmance on `2026-09-02` (Entry 17), Appellee D.C. responded on `2026-09-17` (Entry 18), and subsequent letters regarding the government's Supreme Court certiorari petition were filed on `2026-09-18` to `2026-09-22` (Entries 19–22).

2. **District Court Habeas Record (`C. v. Noem`, S.D.N.Y. No. 1:26-cv-01833-PAE, `docket_id: 72370811`):**
   - Located via `mcp_courtlistener_search` (`type="r"`, `court="nysd"`, `docket_number="1:26-cv-01833"`) and `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=72370811`).
   - Read the full 29-page District Court Opinion & Order (*D.C. v. Noem*, 825 F. Supp. 3d 309 (S.D.N.Y. Mar. 20, 2026), Document 22) via `mcp_courtlistener_read_document` (`recap_document_id=473020076`, chunks 0–4).

3. **Second Circuit En Banc Denial in *Black v. Almodovar; G.M. v. Almodovar* (Nos. 20-3224, 22-70, 156 F.4th 171 (2d Cir. Oct. 24, 2025)):**
   - Located via `mcp_courtlistener_search` (`type="o"`, `court="ca2"`, `q=""Black v. Decker" "1226(c)""`) and read chunks 0–2 of `opinion_id=11176990` via `mcp_courtlistener_read_document`, reviewing Judge Nardini's five-judge dissent from denial of rehearing en banc and the circuit split analysis on 8 U.S.C. § 1226(c) and § 1226(a).

## 3. Web Search (`google_web_search`)

- Executed web searches on `"Genalo" "D. C." "26-379"`, `"Rhoney" "Barbosa da Cunha" "26-104"`, and `"Black v. Decker" "25-886"`, confirming the verbatim Questions Presented in No. 26-379, the Rule 11 certiorari-before-judgment posture as the replacement vehicle for mooted *Genalo v. Black* (No. 25-886), and the extension of Respondent D.C.'s response deadline to December 8, 2026.
