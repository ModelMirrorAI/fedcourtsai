# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-607`
   - Stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Result: 1 row returned (`scotus/73279051`, *Miami Township Board of Trustees v. Roger Dean Gillispie, et al.*, No. 25-607, cert denied 2026-01-26; confirmed that Respondents' citation to "No. 25-607" on page 18 of the BIO for *Perry v. Marteney* was a docket-number typo in the BIO).

2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Result: 10 rows returned (recent OT2026 granted petitions and applications, including *Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12, granted 2026-10-19 after 3 distributions, and *Missionaries of Saint John the Baptist, Inc. v. Frederic*, No. 25-1131, granted 2026-10-01 after 2 distributions).

3. `uv run fedcourts query --court scotus --docket-number 26-307`
   - Stderr: `ranged corpus reads: 715 GET(s), 187432960 byte(s)`
   - Note: `docket-number lookup: no row for 26-307 (scotus)` (0 rows returned).

4. `uv run fedcourts query --court scotus --judge Wilkinson --limit 10`
   - Stderr: `ranged corpus reads: 714 GET(s), 187170816 byte(s)`
   - Result: 0 rows returned.

5. `uv run fedcourts query --court scotus --docket-number 25-77`
   - Stderr: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Result: 1 row returned (`scotus/73272830`, *Stephen Foote, et al. v. Ludlow School Committee, et al.*, No. 25-77, cert denied 2026-04-20 after 13 distributions).

6. `uv run fedcourts query --court scotus --judge King --limit 10`
   - Stderr: `ranged corpus reads: 714 GET(s), 187170816 byte(s)`
   - Result: 0 rows returned.

7. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 15`
   - Stderr: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Result: 15 rows returned (OT2026 petitions distributed for the November 6, 2026 Conference that were denied on November 9, 2026 after 1 or 2 distributions).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca4", case_name="Polk v. Montgomery County Public Schools")`
   - Result: 1 hit (`cluster_id: 10781485`, `opinion_id: 11248108`, *Kimberly Polk v. Montgomery County Public Schools*, No. 25-1136, filed 2026-01-28).

2. `mcp_courtlistener_search(type="o", court="ca11", case_name="Wood v. Florida Department of Education")`
   - Result: 1 hit (`cluster_id: 10622870`, *Katie Wood v. Florida Department of Education*, 142 F.4th 1286, No. 24-11239, filed 2025-07-02).

3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Mirabelli v. Bonta")`
   - Result: 1 hit (`cluster_id: 10802600`, *Mirabelli v. Bonta*, No. 25A810, filed 2026-03-02).

4. `mcp_courtlistener_read_document(opinion_id=11248108, chunk_index=[6, 7, 8, 9, 10, 11, 12], chunk_size=8000)` and `mcp_courtlistener_read_document(opinion_id=11248108, chunk_index=[13, 14, 15, 16], chunk_size=8000)`
   - Result: Read the full text of Judge Wilkinson's dissent in *Polk v. Montgomery County Public Schools* (4th Cir. Jan. 28, 2026), including pages 38–46 of the slip opinion that were truncated in `petition.txt` due to the 35,000-word extraction cap.

5. `mcp_courtlistener_search(type="o", case_name="Bates v. Pakseresht")`
   - Result: 2 hits in the Ninth Circuit (No. 23-4169, panel opinion filed 2025-07-24 and order/opinion filed 2026-02-13).

6. `mcp_courtlistener_search(type="o", case_name="Marteney")` and `mcp_courtlistener_search(type="o", court="ca4", case_name="Krystle Perry v. Stacy Marteney")`
   - Result: Located *Krystle Perry v. Stacy Marteney*, No. 24-2132 (`cluster_id: 10840317`, 4th Cir., filed 2026-04-08).

7. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10802600)` and `mcp_courtlistener_read_document(opinion_id=11269328, chunk_index=[0, 1])` and `mcp_courtlistener_read_document(opinion_id=11269328, chunk_index=[2, 3, 4, 5])`
   - Result: Read *Mirabelli v. Bonta*, 607 U.S. 492 (Mar. 2, 2026) (per curiam opinion, Justice Barrett's concurrence joined by Chief Justice Roberts and Justice Kavanaugh, and Justice Kagan's dissent joined by Justice Jackson), confirming that the Court granted interim relief as to the parent subclasses but denied it as to the teacher subclasses, with only Justices Thomas and Alito noting they would grant the application in full.

8. `mcp_courtlistener_search(type="o", court="ca9", case_name="Theis v. InterMountain Education Service District")`
   - Result: 1 hit (`cluster_id: 10933845`, No. 25-8039, 9th Cir., filed 2026-07-21).

9. `mcp_courtlistener_search(type="o", court="scotus", case_name="Foote v. Ludlow")`, `mcp_courtlistener_search(type="d", court="scotus", case_name="Perry v. Marteney")`, and `mcp_courtlistener_search(type="d", court="scotus", case_name="Wood v. Florida Department of Education")`
   - Result: 0 hits on each of those three searches.
