# Retrieval Log

All external lookups beyond the provisioned case inputs (`record/`) and committed base-rate statpack (`metrics/statpack.md`) are listed below. `mode` is `forward` (`DECIDED_BEFORE` unset). No query targeted the disposition or third-party forecasts of `scotus/9026000598` (`No. 26-598`).

## 1. Corpus CLI Lookups (`uv run fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000598" --event "evt-petition-disposition" --role predictor` and `uv run fedcourts query --help`
   - Transfer: none (metadata/help inspection; confirmed `DECIDED_BEFORE` unset).
2. `uv run fedcourts query --court scotus --citation "22 F.4th 1014" --limit 10`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned: 0 rows (`note:` sparse reporter-citations column on SCOTUS rows).
3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 7 GET(s), 1703936 byte(s)`
   - Returned: 10 recent resolved 2020s SCOTUS rows (`26-6154`, `26A686`, `26A714`, `26A715`, `26A716`, `25-1255`, `26A698`, `25-1238`, `25-1240`, `25-1303`).
4. `uv run fedcourts query --court scotus --docket-number 21-1489`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Returned: 1 row (`scotus/72470823`, *Andrew Ioannidis v. Tom Wolf*, `denied` 2022-10-03; refuted unverified docket number from initial web search summary for *Li*).
5. `uv run fedcourts query --court scotus --docket-number 24-720`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 row (`scotus/72486658`, *Vitaly Korchevsky v. United States*, `denied` 2025-02-24; refuted unverified docket number from initial web search summary for *Shands*).
6. `uv run fedcourts query --court scotus --docket-number 25-988`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 row (`scotus/73281028`, *Stephanie Murrin v. Commissioner of Internal Revenue*, `denied` 2026-06-22; refuted unverified docket number from initial web search summary for *Lissack II*).
7. `uv run fedcourts query --court scotus --docket-number 23-413`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 row (`scotus/72479980`, *Michael Lissack v. Commissioner of Internal Revenue*, originating `cadc` `21-1268`, `disposition: gvr` on `2024-07-02`, `distribution_count: 2`).
8. `uv run fedcourts query --court scotus --docket-number 22-185`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 row (`scotus/72475507`, *Mandy Mobley Li v. Commissioner of Internal Revenue*, originating `cadc` `20-1245`, `disposition: denied` on `2022-10-31`, `distribution_count: 1`).
9. `uv run fedcourts query --court scotus --docket-number 24-715`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: 1 row (`scotus/72486602`, *Thomas Shands v. Commissioner of Internal Revenue*, originating `cadc` `23-1160`, `disposition: denied` on `2025-02-24`, `distribution_count: 1`).
10. `uv run fedcourts query --court scotus --docket-number 16-968`
    - Transfer: `ranged corpus reads: 745 GET(s), 195166208 byte(s)`
    - Returned: 1 row (`scotus/65627542`, `docket_number: 16-968`, `date_filed: 2017-02-03`, `originating_court: ca11`, historical bulk row with `disposition: null`).

## 2. CourtListener MCP Lookups

1. `search(type="o", court="scotus", case_name="Li v. Commissioner", num_results=10)` -> `count: 0`.
2. `search(type="o", court="scotus", case_name="Shands v. Commissioner", num_results=10)` -> `count: 0`.
3. `search(type="o", court="scotus", case_name="Lissack v. Commissioner", num_results=10)` -> `count: 0`.
4. `search(type="o", court="scotus", case_name="Kennedy v. Commissioner", filed_after="2025-07-08", num_results=10)` -> `count: 0` (checked whether consolidated co-appellant Patrick Kennedy had a SCOTUS order on CourtListener).
5. `search(type="o", court="scotus", case_name="Meidinger v. Commissioner", filed_before="2025-07-01", num_results=10)` -> `count: 0`.
6. `search(type="o", court="scotus", q=""7623(b)(4)" OR "22 F.4th 1014" OR "111 F.4th 1" OR "125 F.4th 245"", num_results=10)` -> `count: 0`.
7. `search(type="o", court="scotus", q=""Mandy Mobley Li" OR "Thomas Shands" OR "Michael Lissack" OR "Patrick Kennedy"", num_results=10)` -> `count: 4` (unrelated criminal/habeas orders involving a different Patrick Kennedy, 2008–2016).
8. `search(type="o", court=["ca1","ca2","ca3","ca4","ca5","ca6","ca7","ca8","ca9","ca10","ca11","cadc","cafc"], q=""Li v. Commissioner" "7623(b)"", filed_after="2022-01-11", num_results=20)` -> `count: 0` (exact-string `"Li v. Commissioner"` did not match CourtListener's abbreviated `"Li v. Comm'r"`).
9. `search(type="o", court="scotus", q=""Roy J. Meidinger" OR "Roy Meidinger"", filed_before="2025-07-01", num_results=10)` -> `count: 2` (*Meidinger v. Comm'r of Internal Revenue*, No. 16-968, cert. denied March 6, 2017, 137 S. Ct. 1242; reh'g denied April 17, 2017, 137 S. Ct. 1616).
10. `search(type="d", court="scotus", case_name="Li v. Commissioner", num_results=10)` -> `count: 0`.
11. `search(type="d", court="scotus", case_name="Shands v. Commissioner", num_results=10)` -> `count: 0`.
12. `search(type="d", court="scotus", case_name="Lissack v. Commissioner", num_results=10)` -> `count: 0`.
13. `search(type="d", court="scotus", case_name="Kennedy v. Commissioner", filed_after="2025-07-08", num_results=10)` -> `count: 0`.
14. `search(type="o", court="scotus", case_name="Commissioner v. Zuch", num_results=5)` -> `count: 2` (*Commissioner v. Zuch*, 605 U.S. 422, No. 24-416, decided `2025-06-12`, `opinion_id: 11243427`).
15. `get_endpoint_schema(endpoint_id="dockets")` -> returned `dockets` endpoint schema.
16. `read_document(opinion_id=11243427, chunk_index=0, chunk_size=6000)` -> read syllabus and opening of *Commissioner v. Zuch*, 605 U.S. 422 (2025).
17. `read_document(opinion_id=11243427, chunk_index=1, chunk_size=6000)` -> read lineup of *Zuch* (8–1 majority by Barrett, J.; Gorsuch, J., dissenting) and statutory text.
18. `get_endpoint_schema(endpoint_id="clusters")` -> returned `clusters` endpoint schema.
19. `search(type="o", court="scotus", q=""Li v. Commissioner" OR "Shands v. Commissioner" OR "Lissack v. Commissioner" OR "Kennedy v. Commissioner"", filed_after="2022-01-11", num_results=20)` -> `count: 2` (*Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024)).
20. `read_document(opinion_id=11243427, chunk_index=[5, 6], chunk_size=6000)` -> read conclusion of majority opinion and opening of Justice Gorsuch's dissent in *Commissioner v. Zuch*, 605 U.S. 422 (2025).
21. `search(type="o", court="scotus", case_name="Boechler v. Commissioner", num_results=5)` -> `count: 1` (*Boechler v. Commissioner*, 596 U.S. 199, No. 20-1472, decided `2022-04-21`, Barrett, J.).
22. `search(type="o", court="scotus", q=""Li v. Comm" OR "Shands v. Comm" OR "Meidinger v. United States"", filed_after="2022-06-01", filed_before="2025-07-01", num_results=10)` -> `count: 0`.
23. `search(type="o", court="cadc", q=""7623(b)(4)" "Li v. Comm"", filed_after="2022-01-01", num_results=10)` -> `count: 4` (*Patrick Kennedy v. Cmsnr. IRS & Roy Meidinger, Sr. v. IRS* (`2025-07-08`), *Thomas Shands v. Cmsnr. IRS*, 111 F.4th 1 (`2024-07-26`), and *Michael Lissack v. Cmsnr. IRS*, 68 F.4th 1312 (`2023-05-26`) & remand opinion (`2025-01-10`)).
24. `search(type="o", court="scotus", q="Lissack", num_results=10)` -> `count: 2` (*Loper Bright Enterprises v. Raimondo*, 603 U.S. 369 (2024)).
25. `search(type="o", court="scotus", q="Shands", num_results=10)` -> `count: 40` (historical unrelated "Shands" opinions).
26. `search(type="o", court="scotus", q=""Li v." "Commissioner"", filed_after="2022-01-01", filed_before="2024-01-01", num_results=10)` -> `count: 0`.
27. `search(type="o", court="cadc", docket_number="21-1268", num_results=5)` -> `count: 2` (*Michael Lissack v. Cmsnr. IRS*, `2023-05-26` and `2025-01-10`, `opinion_id: 10778209`).
28. `read_document(opinion_id=10778209, chunk_index=0, chunk_size=4000)` -> read opening of *Lissack v. Commissioner* (`2025-01-10`), confirming remand from Supreme Court post-*Loper Bright* GVR.
29. `search(type="o", court="cadc", docket_number="21-1133", num_results=5)` -> `count: 1` (*Patrick Kennedy v. Cmsnr. IRS & Roy Meidinger, Sr. v. IRS*, `21-1133 & 22-1239`, `2025-07-08`).

## 3. Web Searches (`google_web_search`)

1. `"Li v. Commissioner" "22 F.4th 1014" certiorari denied` -> confirmed certiorari was denied in *Li*; summary misstated docket number as `21-1489` (checked and refuted via corpus query #4).
2. `"Shands v. Commissioner" "111 F.4th 1" certiorari` -> confirmed certiorari was denied in *Shands* and surfaced legislative reform context; summary misstated docket number as `24-720` (checked and refuted via corpus query #5).
3. `"Lissack v. Commissioner" "125 F.4th 245" certiorari` -> surfaced `No. 23-413` GVR in *Lissack I* (verified via corpus query #7); summary misstated `25-988` as a second *Lissack* petition (checked and refuted via corpus query #6, which showed `25-988` was *Murrin v. Commissioner*).
4. `site:supremecourt.gov "Mandy Mobley Li" OR "Li v. Commissioner of Internal Revenue" "22 F.4th 1014"` -> identified `No. 22-185` (verified via corpus query #8: `denied` `2022-10-31`).
5. `site:supremecourt.gov "Thomas Shands" "Commissioner of Internal Revenue"` -> summarized *Shands* certiorari denial and questions presented.
6. `site:supremecourt.gov "Michael Lissack" "125 F.4th 245"` -> confirmed `No. 23-413` GVR and noted D.C. Circuit decision in *Estate of Joseph A. Insinga v. Commissioner* (Aug. 8, 2025).
7. `site:supremecourt.gov/DocketPDF "Thomas Shands" "Commissioner"` -> identified `No. 24-715` (verified via corpus query #9: `denied` `2025-02-24`).
8. `site:supremecourt.gov/DocketPDF "Estate of Joseph A. Insinga" "Commissioner"` -> indicated *Insinga* was attached as an appendix in *Daniel Allen Villa v. Commissioner*, `No. 26-5774` (IFP petition docketed Oct. 7, 2026).
9. `"H.R. 7959" "IRS Whistleblower Program Improvement Act"` -> confirmed H.R. 7959 (119th Cong.) passed the House 346–10 on April 27, 2026 and was referred to the Senate Finance Committee.
