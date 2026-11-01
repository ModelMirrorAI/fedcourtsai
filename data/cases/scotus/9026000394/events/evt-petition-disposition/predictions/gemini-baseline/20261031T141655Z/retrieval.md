# Retrieval Log — `scotus/9026000394` (`evt-petition-disposition`)

## 1. Corpus Priors (`fedcourts query`)

### Commands and Transfer Lines
1. `uv run fedcourts query --court scotus --docket-number 25-1013`
   - Transfer stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
2. `uv run fedcourts query --court scotus --docket-number 23-675`
   - Transfer stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
3. `uv run fedcourts query --court scotus --docket-number 23-702`
   - Transfer stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer stderr: `ranged corpus reads: 34 GET(s), 8912896 byte(s)`

### Retrieved Corpus Cases and What Was Learned
- **`scotus/73281060` — *Official Committee of Asbestos Claimants of Bestwall LLC v. Bestwall LLC*, No. 25-1013 (OT2025):**
  - Originating from the Fourth Circuit (`originating_docket_number: "24-1493"`), filed February 24, 2026, distributed once (`distribution_count: 1`), and **denied** on June 1, 2026 (`disposition: "denied"`).
  - Supported by a closely overlapping amicus coalition (Public Justice, Group of Bankruptcy Law Professors, Bankruptcy and Legal History Professors, Prof. D. Theodore Rave, Senators Durbin/Whitehouse/Hawley represented by Deepak Gupta, the Asbestos Creditors' Committees in the DBMP and Aldrich Bankruptcies, and the American Association for Justice).
  - **Relevance:** Demonstrates that the Supreme Court denied review just five months ago in the sibling Fourth Circuit "Texas Two-Step" asbestos bankruptcy case (*Bestwall*) despite heavy amicus support from nearly the same filers appearing in *Herlihy v. DBMP, LLC*.
- **`scotus/72482019` — *Official Committee of Asbestos Claimants v. Bestwall LLC, et al.*, No. 23-675 (OT2023):**
  - Originating from the Fourth Circuit (`22-1127, 22-1135`), filed December 22, 2023, distributed once, and **denied** on May 13, 2024. Amici included Members of Congress (represented by Deepak Gupta) and North Carolina, et al.
- **`scotus/72482323` — *Sander L. Esserman, in His Official Capacity as Future Claims Representative v. Bestwall LLC, et al.*, No. 23-702 (OT2023):**
  - Companion petition to No. 23-675, **denied** on May 13, 2024.
- **Recent OT2026 Cert Grants (`--court scotus --era 2020s --disposition granted --limit 10`):**
  - Reviewed recent OT2026 cert grants (e.g., `scotus/9026000012` *Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12, granted after 3 distributions; `scotus/9026000204` *Department of Justice v. McNutt*, No. 26-204, granted after 2 distributions; `scotus/73500246` *Blanche v. Ozurumba*, No. 25-1343, granted after 2 distributions) to confirm typical distribution/relist patterns prior to a grant.

## 2. Open-Web CourtListener MCP Queries

1. `mcp_courtlistener_search(type="o", citation="148 F.4th 233", num_results=5)`
   - Returned `count: 0` (the Fourth Circuit's *Bestwall* decision citation and holding were already detailed in Judge King's dissent in `record/documents/appendix.txt` at App. 19a, 43a n.10, and 45a, and the Supreme Court petition disposition was retrieved directly from the local corpus under No. 25-1013).
