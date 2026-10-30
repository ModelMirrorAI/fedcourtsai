# Retrieval Log (`scotus/73538544` — `evt-petition-disposition`)

## 1. Corpus Queries (`uv run fedcourts query`)

1. **Recent SCOTUS GVR dispositions (limit 20):**
   - **Command:** `uv run fedcourts query --court scotus --disposition gvr --limit 20`
   - **Rows returned:** 20
   - **Stderr transfer line:** `ranged corpus reads: 53 GET(s), 13697024 byte(s)`
   - **Relevance:** Confirmed the structural profile of OT 2025 / early OT 2026 GVR dispositions in the corpus (typically resolving at `distribution_count` 1–4, including state intermediate appellate courts such as `scotus/9026000139`, *Monsanto Co. v. Dennis*, GVR'd on Oct. 13, 2026 from the California Court of Appeal).

2. **Lookup by reporter citation for *Montgomery v. Caribe Transport II, LLC*:**
   - **Command:** `uv run fedcourts query --court scotus --citation "146 S. Ct. 1199" --citation "608 U.S. 219" --limit 10`
   - **Rows returned:** 0 (note indicated only 200 SCOTUS rows carry reporter citations in the `citations` column)
   - **Stderr transfer line:** `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - **Relevance:** Came back empty because `citations` is sparsely populated for recent OT 2025 merits decisions; substantive holdings of *Montgomery* were instead drawn directly from the provisioned filings (`petition.txt` and `brief-in-opposition.txt`).

3. **Target docket lookup (`25-1421`):**
   - **Command:** `uv run fedcourts query --court scotus --docket-number 25-1421`
   - **Rows returned:** 1 (`scotus/73538544`)
   - **Stderr transfer line:** `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - **Relevance:** Verified the corpus metadata row for *Christina Casarez v. Irigoyen Farms, Inc., et al.* (`docket_number: "25-1421"`, `distribution_count: 2`, `distributed_for_conference: "2026-11-13"`, counsel of record Kevin G. Little, Edward R. Hugo, and Roman Martinez V).

4. **Recent SCOTUS granted petitions (limit 50):**
   - **Command:** `uv run fedcourts query --court scotus --disposition granted --limit 50`
   - **Rows returned:** 50
   - **Stderr transfer line:** `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - **Relevance:** Provided baseline context on recent OT 2025 / OT 2026 plenary grants and their procedural markers.

5. **Recent SCOTUS summary reversals (limit 20):**
   - **Command:** `uv run fedcourts query --court scotus --disposition summary-reversal --limit 20`
   - **Rows returned:** 0
   - **Stderr transfer line:** `ranged corpus reads: 861 GET(s), 225509376 byte(s)`
   - **Relevance:** Confirmed the extreme rarity of standalone `summary-reversal` dispositions in the corpus, reinforcing that pre-decision lower-court reliance on subsequently abrogated circuit authority is handled via `gvr` rather than `summary-reversal`.

6. **Extended SCOTUS GVR dispositions (limit 50):**
   - **Command:** `uv run fedcourts query --court scotus --disposition gvr --limit 50`
   - **Rows returned:** 50
   - **Stderr transfer line:** `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - **Relevance:** Surveyed 50 recent GVR dispositions across May–October 2026 conferences, confirming the frequency and procedural pattern of GVRs following intervening merits decisions.

## 2. CourtListener MCP Calls

1. **`mcp_courtlistener_search` (Opinion search for *Montgomery v. Caribe Transport*):**
   - **Parameters:** `type="o"`, `court="scotus"`, `case_name="Montgomery v. Caribe Transport"`, `num_results=10`, `fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "docketNumber", "snippet"]`
   - **Result:** Failed with `HTTP 429: Request was throttled. Rate limit exceeded: 1400/day. Expected available in 2538 seconds.`

2. **`mcp_courtlistener_search` (Opinion search for orders citing *Montgomery v. Caribe Transport* after 2026-05-14):**
   - **Parameters:** `type="o"`, `court="scotus"`, `q=""Montgomery v. Caribe" OR "Caribe Transport""`, `filed_after="2026-05-14"`, `num_results=20`, `fields=["id", "cluster_id", "caseName", "dateFiled", "citation", "docketNumber", "snippet"]`
   - **Result:** Failed with `HTTP 429: Request was throttled. Rate limit exceeded: 1400/day. Expected available in 2538 seconds.`

## 3. Summary of What Informed `reasoning.md`

- The provisioned case filings in `data/cases/scotus/73538544/record/documents/` (`petition.txt`, `brief-in-opposition.txt`, `cert-reply.txt`, and `questions-presented.txt`) and the docket snapshot (`2026-10-29.json`) provided comprehensive, primary-source detail on both the California Court of Appeal's unpublished decision (reproducing Pet. App. 1a–14a in `petition.txt`), this Court's intervening decision in *Montgomery v. Caribe Transport II, LLC*, 608 U.S. 219 (2026), and Respondent Walmart's October 13, 2026 post-CFR brief explicitly agreeing that the Court should enter a GVR order in light of *Montgomery*.
- The corpus queries (`--disposition gvr` and `--disposition summary-reversal`) provided structural base-rate confirmation for `gvr` versus `summary-reversal` or plenary `granted`.
