# Retrieval Log

## Corpus CLI (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000658" --event "evt-motion-disposition" --role predictor`
   - Resolved cell paths (`scotus/9526000658`, `data/cases/scotus/9526000658/events/evt-motion-disposition/event.yaml`).
2. `uv run fedcourts query --help`
   - Inspected CLI options.
3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned 10 recent resolved SCOTUS priors from the 2020s era, including 8 substantive emergency applications (`26A623`, `26A634`, `26A637`, `26A644`, `26A636`, `26A602`, `26A612`, `26A619`), all denied.
4. `uv run fedcourts query --court scotus --docket-number 26A658`
   - `ranged corpus reads: 16 GET(s), 4063232 byte(s)`
   - Returned the open corpus row for `scotus/9526000658` (`26A658`, `Paul Schultz v. H. Jason Gold`, `disposition: null`, `response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0`, `last_live_polled: "2026-11-09"`).
5. `uv run fedcourts query --court scotus --citation "542 U.S. 367" --limit 5`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).
6. `uv run fedcourts query --court ca4 --judge Wilkinson --limit 5`
   - `ranged corpus reads: 93 GET(s), 24379392 byte(s)`
   - Returned 0 rows (circuit judge lists withheld on bulk slice).
7. `uv run fedcourts query --court scotus --docket-number 26A657`
   - `ranged corpus reads: 18 GET(s), 4587520 byte(s)`
   - Returned companion open application `scotus/9526000657` (`26A657`, `Paul Schultz v. Kevin McCarthy`, `originating_court: "ca4"`, `originating_docket_number: "26-2406"`, `disposition: null`).
8. `uv run fedcourts query --court scotus --docket-number 26A659`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned unrelated extension application `26A659` (`Kevin Duden v. Washington, et al.`).
9. `uv run fedcourts query --court scotus --docket-number 26A660`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned unrelated extension application `26A660` (`Jonathan D. Carr v. Kansas`).
10. `uv run fedcourts query --court scotus --docket-number 26A656`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned unrelated extension application `26A656` (`Melchor Magdaleno-Garcia v. Texas`).
11. `uv run fedcourts query --court scotus --docket-number 26A655`
    - `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned unrelated extension application `26A655` (`M. P. v. Arizona Department of Child Safety`).

## CourtListener MCP Lookups

1. `search(type="r", case_name="Schultz v. Gold", num_results=10)`
   - Returned 6 RECAP dockets in E.D. Va., Bankr. E.D. Va., and the Fourth Circuit (`1:26-cv-02804`, `26-01022`, `25-2195`, `1:25-cv-01498`, `1:25-cv-01336`, `1:25-cv-00927`).
2. `search(type="o", case_name="Schultz v. Gold", num_results=10)`
   - Returned 1 unrelated 1907 opinion (*Schultz v. Highland Gold Mines Co.*).
3. `search(type="d", docket_number="26-2404", num_results=10)`
   - Identified *In re: Paul Schultz*, No. 26-2404, in the U.S. Court of Appeals for the Fourth Circuit (`docket_id: 74925991`).
4. `get_endpoint_item(endpoint_id="dockets", item_id=74925991, fields=[..., "originating_court_information"])`
   - Returned field-validation error (`originating_court_information` invalid; use `original_court_info`).
5. `call_endpoint(endpoint_id="docket-entries", query={"docket": 74925991, ...})`
   - Returned 4 docket entries on 4th Cir. No. 26-2404, including Entry 10 (Oct. 22, 2026 unpublished per curiam opinion), Entry 11 (Oct. 22, 2026 judgment order), and Entry 15 (Nov. 4, 2026 court order).
6. `call_endpoint(endpoint_id="docket-entries", query={"docket": 74708354, ...})`
   - Returned 0 entries for E.D. Va. `1:26-cv-02804` (`docket_id: 74708354`).
7. `call_endpoint(endpoint_id="docket-entries", query={"docket": 73256191, ...})`
   - Returned 20 docket entries in *Schultz v. H. Jason Gold, Former Chapter 7 Trustee*, Adv. No. 26-01022 (Bankr. E.D. Va.), including Entry 69 (Aug. 5, 2026 order dismissing adversary proceeding), Entry 72 (Aug. 17, 2026 notice of appeal), and Entry 79 (Aug. 25, 2026 order on motion to expedite and motion to stay).
8. `search(type="o", q='"Paul Schultz" "Jason Gold"')`
   - Returned 0 results.
9. `get_endpoint_item(endpoint_id="dockets", item_id=74925991, fields=["id", "case_name", "docket_number", "court", "date_filed", "date_terminated", "cause", "nature_of_suit", "appeal_from_str", "panel_str", "clusters"])`
   - Returned docket metadata for *In re: Paul Schultz* (4th Cir. No. 26-2404) linking to cluster `11044676`.
10. `get_endpoint_item(endpoint_id="dockets", item_id=71581592, fields=["id", "case_name", "docket_number", "court", "date_filed", "date_terminated", "cause", "nature_of_suit", "appeal_from_str", "panel_str", "clusters"])`
    - Returned docket metadata for *Paul Schultz v. H. Gold* (4th Cir. No. 25-2195) linking to cluster `10927064`.
11. `search(type="o", docket_number="26-2404")`
    - Returned 0 results in opinion search index.
12. `search(type="o", docket_number="25-2195")`
    - Returned 1 unrelated Iowa opinion.
13. `get_endpoint_item(endpoint_id="clusters", item_id=11044676, fields=["id", "case_name", "date_filed", "judges", "sub_opinions", "precedential_status"])`
    - Returned cluster `11044676` (*In re: Paul Schultz*, filed `2026-10-22`, `sub_opinions: [".../opinions/11512446/"]`).
14. `get_endpoint_item(endpoint_id="clusters", item_id=10927064, fields=["id", "case_name", "date_filed", "judges", "sub_opinions", "precedential_status"])`
    - Returned cluster `10927064` (*Paul Schultz v. H. Gold*, filed `2026-07-10`, `sub_opinions: [".../opinions/11394602/"]`).
15. `read_document(opinion_id=11512446)`
    - Read full text of *In re: Paul Schultz*, No. 26-2404 (4th Cir. Oct. 22, 2026) (unpublished per curiam opinion by Judges Wilkinson, King, and Rushing denying mandamus petition seeking recusal of E.D. Va. district judge in `1:26-cv-02804-LMB-IDD` and denying stay motions as moot).
16. `read_document(opinion_id=11394602)`
    - Read full text of *Paul Schultz v. H. Gold*, Nos. 25-2195 et al. (4th Cir. July 10, 2026) (unpublished per curiam opinion resolving eight consolidated bankruptcy appeals).
17. `get_endpoint_item(endpoint_id="dockets", item_id=71328181, fields=["id", "case_name", "docket_number", "court", "date_filed", "date_terminated", "cause", "nature_of_suit", "clusters"])`
    - Returned docket metadata for *Schultz v. Gold*, No. `1:25-cv-01498` (E.D. Va.).
18. `search(type="d", court="scotus", case_name="Schultz", num_results=10)`
    - Returned 0 results.
19. `search(type="d", court="ca4", case_name="Schultz", num_results=20)`
    - Returned 20 of 31 Fourth Circuit dockets matching `Schultz`, including companion mandamus petitions `26-2404`, `26-2405`, and `26-2406`.
20. `get_endpoint_item(endpoint_id="dockets", item_id=74925990, fields=["id", "case_name", "docket_number", "court", "date_filed", "date_terminated", "clusters"])`
    - Returned docket metadata for *In re: Paul Schultz*, No. 26-2405 (4th Cir., cluster `11044675`).
21. `get_endpoint_item(endpoint_id="dockets", item_id=74925989, fields=["id", "case_name", "docket_number", "court", "date_filed", "date_terminated", "clusters"])`
    - Returned docket metadata for *In re: Paul Schultz*, No. 26-2406 (4th Cir., cluster `11046332`).
