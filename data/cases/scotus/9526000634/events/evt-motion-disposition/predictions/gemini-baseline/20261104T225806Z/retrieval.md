# Retrieval Log: `scotus/9526000634` (`evt-motion-disposition`)

## 1. Local Corpus Queries (`uv run fedcourts query`)

All corpus queries were executed against `corpus/corpus.db` in forward mode (`cutoff: 2026-11-04`).

1. **Query 1 — Linked Certiorari Petition (`26-6051`)**:
   - **Command**: `uv run fedcourts query --court scotus --docket-number 26-6051`
   - **Filters**: `court=scotus`, `docket_number=26-6051`
   - **Transfer line**: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - **Result & Relevance**: Returned `scotus/9026006051` (*Jesse Guardado v. Richard Comerford, Secretary, Florida Department of Corrections, et al.*, `docket_number: "26-6051"`, `capital_case: true`, `date_filed: "2026-11-03"`, `originating_court: "ca11"`, `originating_docket_number: "26-14027"`). Confirmed the originating Eleventh Circuit docket number (`26-14027`) and capital certiorari linkage.

2. **Query 2 — Recent Resolved 2020s SCOTUS Denials**:
   - **Command**: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - **Filters**: `court=scotus`, `era=2020s`, `disposition=denied`, `limit=10`
   - **Transfer line**: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - **Result & Relevance**: Returned 10 recent OT2026 substantive applications (`26A602`, `26A612`, `26A619`, `26A606`, `26A613`, `26A617`, `26A618`, `26A499`, `26A535`, `26A532`) all denied between October 23 and November 3, 2026, including applications from Florida courts (`26A602`, `26A535`) and an application where a response was requested (`26A499`, *Louisiana v. Devon Energy Production Co.*).

3. **Query 3 — Recent Resolved 2020s SCOTUS Grants**:
   - **Command**: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - **Filters**: `court=scotus`, `era=2020s`, `disposition=granted`, `limit=10`
   - **Transfer line**: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - **Result & Relevance**: Returned 10 recent grants, including two OT2026 substantive interim applications (`26A512`, *Scanlan v. Coalition for Open Democracy*, and `26A476`, *FCC v. Brown*). Confirmed that substantive interim grants in OT2026 involved government/state-official applicants with formal referral to the full Court (`referred_to_court: true`) and amicus participation (`amicus_briefs: 1`).

4. **Query 4 — Citation Lookup Probe (`146 S. Ct. 755`)**:
   - **Command**: `uv run fedcourts query --court scotus --citation "146 S. Ct. 755" --limit 5`
   - **Filters**: `court=scotus`, `citation="146 S. Ct. 755"`, `limit=5`
   - **Transfer line**: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - **Result & Relevance**: Returned 0 rows (with CLI note that reporter citations are populated on only 200 rows in the SCOTUS corpus table).

5. **Query 5 — Judge Filter Probe (`Clarence Thomas`)**:
   - **Command**: `uv run fedcourts query --court scotus --judge "Clarence Thomas" --era 2020s --disposition denied --limit 10`
   - **Filters**: `court=scotus`, `judge="Clarence Thomas"`, `era=2020s`, `disposition=denied`, `limit=10`
   - **Transfer line**: `ranged corpus reads: 678 GET(s), 177733632 byte(s)`
   - **Result & Relevance**: Returned 0 rows (confirming `judges` array is generally unpopulated on summary application denial rows).

6. **Queries 6–19 — Contemporary `25A` and `26A` Application Probes**:
   - **Commands & Transfer Lines**:
     - `uv run fedcourts query --court scotus --docket-number 25A715` -> `ranged corpus reads: 10 GET(s), 2621440 byte(s)` (returned `scotus/73280092`, extension granted)
     - `uv run fedcourts query --court scotus --docket-number 25A780` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/73280150`, extension granted)
     - `uv run fedcourts query --court scotus --docket-number 26A633` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000633`, *Brown v. Colorado*, extension pending)
     - `uv run fedcourts query --court scotus --docket-number 26A635` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000635`, *Speer v. Texas*, capital extension pending)
     - `uv run fedcourts query --court scotus --docket-number 26A590` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000590`, extension granted)
     - `uv run fedcourts query --court scotus --docket-number 26A631` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000631`, *Gonzales v. Texas*, capital extension pending)
     - `uv run fedcourts query --court scotus --docket-number 26A632` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000632`, *Smith v. Florida*, extension pending)
     - `uv run fedcourts query --court scotus --docket-number 26A625` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000625`, extension granted)
     - `uv run fedcourts query --court scotus --docket-number 26A626` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000626`, extension granted)
     - `uv run fedcourts query --court scotus --docket-number 26A627` -> `ranged corpus reads: 677 GET(s), 177471488 byte(s)` (no row in corpus)
     - `uv run fedcourts query --court scotus --docket-number 26A628` -> `ranged corpus reads: 10 GET(s), 2621440 byte(s)` (returned `scotus/9526000628`, extension pending)
     - `uv run fedcourts query --court scotus --docket-number 26A629` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000629`, extension pending)
     - `uv run fedcourts query --court scotus --docket-number 26A630` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9526000630`, extension pending)
     - `uv run fedcourts query --court scotus --docket-number 26-6050` -> `ranged corpus reads: 0 GET(s), 0 byte(s)` (returned `scotus/9026006050`, *Woodall v. Plappert*, capital cert petition pending)
   - **Relevance**: Confirmed that `26A634` is Guardado's sole pending application in the corpus and has no companion application on which relief could render `26A634` moot.

---

## 2. CourtListener MCP Calls

1. **`mcp_courtlistener_search` (Call 1 — CA11 RECAP Docket `26-14027`)**:
   - **Parameters**: `type="r"`, `court="ca11"`, `docket_number="26-14027"`, `fields=["caseName", "docketNumber", "dateFiled", "court_id", "id"]`
   - **Result**: Returned 1 docket (*Jesse Guardado v. Secretary, Department of Corrections*, `ca11`, `26-14027`, filed `2026-10-30`).

2. **`mcp_courtlistener_search` (Call 2 — CA11 Opinion Search for Guardado)**:
   - **Parameters**: `type="o"`, `court="ca11"`, `q="Guardado etomidate Comerford"`, `fields=["caseName", "docketNumber", "dateFiled", "cluster_id", "opinions"]`
   - **Result**: Returned 0 results (the Eleventh Circuit's November 2, 2026 unpublished order is indexed on the RECAP docket rather than the opinions collection).

3. **`mcp_courtlistener_search` (Call 3 — CA11 RECAP Documents on `26-14027`)**:
   - **Parameters**: `type="r"`, `court="ca11"`, `docket_number="26-14027"`, `fields=["caseName", "docketNumber", "docket_id", "recap_documents"]`
   - **Result**: Returned `docket_id: 74910150` with 3 RECAP documents, including Document `13-1` (`id: 500108161`, 20 pages, filed `2026-11-02`, opinion/order denying stay of execution).

4. **`mcp_courtlistener_search` (Call 4 — CA11 Opinion Search for Etomidate / Warrant-Eligible Precedent)**:
   - **Parameters**: `type="o"`, `court="ca11"`, `q='etomidate "warrant-eligible" OR "Heath" OR "Trotter"'`, `fields=["caseName", "docketNumber", "dateFiled", "cluster_id", "opinions"]`
   - **Result**: Returned 2 clusters for *Bobby Joe Long v. Secretary, Department of Corrections*, 924 F.3d 1171 (11th Cir. 2019) (`cluster_id: 4622513` and `4622317`), the foundational Eleventh Circuit precedent on Florida's etomidate protocol and equitable delay.

5. **`mcp_courtlistener_read_document` (Call 5 — Read CA11 Order in `26-14027`)**:
   - **Parameters**: `recap_document_id=500108161`
   - **Result**: Returned the full 20-page (36,694 chars) Eleventh Circuit order and Judge Jill Pryor's concurrence entered November 2, 2026. Directly informed our analysis of the district court's factual findings, *in camera* lot/invoice verification, independent procedural bars, and prior 2026 Florida stay denials (*Trotter v. Florida*, 146 S. Ct. 755 (2026)).

6. **`mcp_courtlistener_search` (Call 6 — CA11 RECAP Search by Party Name `Comerford`)**:
   - **Parameters**: `type="r"`, `court="ca11"`, `party_name="Comerford"`, `fields=["caseName", "docketNumber", "dateFiled", "docket_id", "recap_documents"]`
   - **Result**: Returned 2 unrelated dockets (`21-14252`, *Abdoo v. Glenmark Pharmaceuticals*, and `20-12412`, *Gaston v. Comerford*).

7. **`mcp_courtlistener_search` (Call 7 — SCOTUS Opinion Search for `Trotter v. Florida` / `146 S. Ct. 755`)**:
   - **Parameters**: `type="o"`, `court="scotus"`, `q='"Trotter v. Florida" OR "146 S. Ct. 755" OR "etomidate"'`, `fields=["caseName", "docketNumber", "dateFiled", "citation", "cluster_id", "opinions"]`
   - **Result**: Returned 1 older 1997 cert denial (*Trotter v. Florida*, 522 U.S. 876 (1997)); the 2026 order-list statement (146 S. Ct. 755) is quoted directly in the Eleventh Circuit's order (`recap_document_id=500108161` at p. 20).

8. **`mcp_courtlistener_search` (Calls 8 & 9 — SCOTUS 2026 Opinion Searches for `Trotter` and `Heath`)**:
   - **Parameters**: `type="o"`, `court="scotus"`, `case_name="Trotter"`, `filed_after="2026-01-01"` (0 results) and `case_name="Heath"`, `filed_after="2026-01-01"` (0 results).

9. **`mcp_courtlistener_search` (Call 10 — Florida Supreme Court 2026 Opinion Search for `Guardado`)**:
   - **Parameters**: `type="o"`, `court="fla"`, `case_name="Guardado"`, `filed_after="2026-01-01"`, `fields=["caseName", "docketNumber", "dateFiled", "citation", "cluster_id", "opinions"]`
   - **Result**: Returned 1 opinion (*Jesse Guardado v. State of Florida*, No. `SC2026-1605`, `cluster_id: 11049070`, `opinion_id: 11516852`, filed `2026-10-29`).

10. **`mcp_courtlistener_read_document` (Call 11 — Read Florida Supreme Court Opinion in `SC2026-1605`)**:
    - **Parameters**: `opinion_id=11516852`
    - **Result**: Returned the full 19-page (32,127 chars) per curiam opinion and Justice Tanenbaum's concurrence affirming the denial of successive postconviction relief and denying a stay of execution.

11. **`mcp_courtlistener_search` (Call 12 — Middle District of Florida RECAP Search for `Guardado`)**:
    - **Parameters**: `type="r"`, `court="flmd"`, `party_name="Guardado"`, `fields=["caseName", "docketNumber", "dateFiled", "docket_id", "recap_documents"]`
    - **Result**: Returned 15 dockets, including *Guardado v. Secretary, Florida Department of Corrections*, `3:26-cv-02596` (`docket_id: 74859241`, filed `2026-09-28`), confirming the district court filing date and early procedural orders.

---

## 3. Web Retrieval (`web_fetch`)

1. **Supreme Court Docket `26A634`**:
   - **URL**: `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26a634.html`
   - **Result**: Confirmed `26A634` is pending as of November 4, 2026, linked with `26-6051`, with the application submitted to Justice Thomas on November 3, 2026 and the response of Richard Comerford submitted on November 4, 2026.

2. **Supreme Court Docket `26-6051`**:
   - **URL**: `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26-6051.html`
   - **Result**: Confirmed `26-6051` is pending as of November 4, 2026, with the petition and IFP motion filed November 3, 2026 and Respondent's brief in opposition submitted November 4, 2026.

3. **Supreme Court Docket `26A627` (Unrelated Neighbour Check)**:
   - **URL**: `https://www.supremecourt.gov/search.aspx?filename=/docket/docketfiles/html/public/26a627.html`
   - **Result**: Confirmed `26A627` is an unrelated California capital extension application (*Theodore Churchill Shove, III v. California*).
