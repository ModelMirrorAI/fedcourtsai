# Retrieval Log: `scotus/9026000157` (`evt-petition-disposition`)

## 1. Local Corpus Queries (`fedcourts query`)

1. **Query for recent church-autonomy cert petition *United States Conference of Catholic Bishops v. O'Connell* (No. 25-849):**
   - **Command:** `uv run fedcourts query --court scotus --docket-number "25-849" --limit 5`
   - **Stderr transfer stats:** `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - **Result:** Retrieved `scotus/73280351` (*United States Conference of Catholic Bishops v. David O'Connell*, No. 25-849), filed `2026-01-15`, originating from the D.C. Circuit (`23-7173`), distributed 4 times (`distribution_count: 4`), and `denied` on `2026-05-26` despite extensive amicus participation (including several of the same amici appearing in No. 26-157: Anglican Church in North America and Sharon Fast Gustafson / Rachel N. Morrison).

2. **Query for recent 2020s SCOTUS granted petitions:**
   - **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - **Stderr transfer stats:** `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
   - **Result:** Retrieved recent OT2026 granted cert petitions (`scotus/9026000012`, No. 26-12; `scotus/9026000204`, No. 26-204; `scotus/73281386`, No. 25-1103) and substantive applications (`26A512`, `26A476`), showing typical distribution counts (2–3 distributions) for early OT2026 cert grants.

3. **Query for linked extension application `25A1307`:**
   - **Command:** `uv run fedcourts query --court scotus --docket-number "25A1307" --limit 5`
   - **Stderr transfer stats:** `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - **Result:** Retrieved `scotus/73389315` (*Jasvinder Singh, et al. v. Second Judicial District Court of Nevada, Washoe County, et al.*, No. 25A1307), confirming it was a routine time-extension application (`application_kind: "extension"`) granted on `2026-05-26`.

## 2. External Legal Research (`courtlistener` MCP)

1. **Search for *Lutheran Church—Missouri Synod v. Christian* (5th Cir. 2026):**
   - **Tool:** `mcp_courtlistener_search` (`type="o"`, `case_name="Lutheran Church"`, `filed_after="2025-01-01"`)
   - **Result:** Confirmed the Fifth Circuit's published decision in *Lutheran Church v. Christian*, No. 25-50130 (5th Cir. June 4, 2026) (`cluster_id: 10870215`), which Petitioners rely on as the most recent federal circuit decision deepening the split after the denial of certiorari in *O'Connell* (May 26, 2026).

2. **Search for *McRaney* opinions after 2025-01-01:**
   - **Tool:** `mcp_courtlistener_search` (`type="o"`, `case_name="McRaney"`, `filed_after="2025-01-01"`)
   - **Result:** 0 additional opinions returned under that exact filter.
