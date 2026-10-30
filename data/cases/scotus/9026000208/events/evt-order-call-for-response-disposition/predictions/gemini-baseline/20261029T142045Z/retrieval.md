# Retrieval Log Summary: *George Anibowei v. Todd Blanche, Attorney General, et al.* (No. 26-208)

## 1. Local Corpus Queries (`uv run fedcourts query`)

1. **`uv run fedcourts query --court scotus --docket-number 23-199`**
   - **Purpose:** Inspect the prior certiorari petition in this exact litigation (*George Anibowei v. Alejandro N. Mayorkas*, No. 23-199, `scotus/72479748`).
   - **Result:** Confirmed that No. 23-199 (filed Sept. 1, 2023 from 5th Cir. No. 20-10059, with Andrew Timothy Tutt as counsel of record and Cato Institute as amicus) was distributed twice and denied certiorari on January 8, 2024.
2. **`uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`**
   - **Purpose:** Review recent SCOTUS cert grants and their distribution/salience profiles for baseline calibration.
3. **`uv run fedcourts query --court scotus --docket-number 20-1043` & `--docket-number 20-1505` & `--docket-number 26-208`**
   - **Purpose:** Check prior Supreme Court border-cell-phone-search petitions cited in the petition (*United States v. Cano*, No. 20-1043, `scotus/72465054`, and *Merchant v. Mayorkas*, No. 20-1505, `scotus/72465554`), as well as the index row for `26-208` (`scotus/9026000208`).
   - **Result:** Confirmed that both *Cano* (even though brought by the United States as petitioner) and *Merchant* (brought by travelers challenging the same CBP/ICE directives) were denied certiorari on June 28, 2021.
4. **`uv run fedcourts query --court scotus --judge "Andrew Timothy Tutt" --limit 10` & `--citation "103 F.4th 1303" --limit 5`**
   - **Purpose:** Check whether any other SCOTUS corpus rows matched counsel or the Seventh Circuit citation; returned empty (as `--judge` filters judicial panels and `--citation` filters a row's own parallel cites).

## 2. CourtListener MCP Queries

- Attempted three `search` calls for lower-court opinions cited in the petition (*Malik v. U.S. Department of Homeland Security*, *United States v. Mendez*, and *Belmonte Cardozo*); all three returned HTTP 429 (`Rate limit exceeded: 1400/day`).
- No retry was needed because the full text of *Malik v. U.S. Department of Homeland Security*, 78 F.4th 191 (5th Cir. 2023), *Anibowei I*, 70 F.4th 898 (5th Cir. 2023), the Fifth Circuit's unpublished decision below, and the district court's dismissal order are all included in full in the provisioned `record/documents/appendix.txt`.
