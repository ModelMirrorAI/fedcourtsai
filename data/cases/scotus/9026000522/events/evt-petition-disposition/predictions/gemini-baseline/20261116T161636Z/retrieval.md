# Retrieval Log

## Local Path & CLI Help Checks (No Remote Reads)

- `uv run fedcourts paths --court "scotus" --docket "9026000522" --event "evt-petition-disposition" --role predictor`
- `uv run fedcourts query --help`

## Corpus CLI Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --limit 25`
   - Transfer: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Result: Returned 25 recent SCOTUS dockets (primarily November 16, 2026 cert denials and GVRs from the November 13 Conference, showing typical `distribution_count` patterns).
2. `uv run fedcourts query --court scotus --docket-number 25-819`
   - Transfer: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned `scotus/73279958` (*Jeanne Hedgepeth v. James A. Britton, et al.*, originating from `ca7` No. 24-1427, counsel Paul D. Clement, 7 amicus filers, `distribution_count: 2`, `disposition: "denied"` on `2026-05-18`).
3. `uv run fedcourts query --court scotus --docket-number 24-355`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/70670981` (*Kari MacRae v. Matthew Mattos, et al.*, originating from `ca1` No. 23-1817, 3 amicus filers, `distribution_count: 16`, `disposition: "denied"` on `2025-06-30`).
4. `uv run fedcourts query --court scotus --docket-number 26-522`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/9026000522` (*Sam Inendino v. Annette Nance-Holt, et al.*, open, `distribution_count: 1`, `salience_score: 0.0182`, matching the provisioned snapshot).
5. `uv run fedcourts query --court scotus --disposition granted --limit 15`
   - Transfer: `ranged corpus reads: 26 GET(s), 6750208 byte(s)`
   - Result: Returned 15 recent SCOTUS granted petitions and substantive applications from October–November 2026 for comparison of counsel, amicus counts, and distribution counts.
6. `uv run fedcourts query --court scotus --disposition gvr --limit 10`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm local corpus service cache)
   - Result: Returned 10 recent SCOTUS GVR dispositions from October–November 2026.
7. `uv run fedcourts query --court scotus --party "Hussey" --limit 5` (first iteration of loop over party names)
   - Transfer: none (`Exit Code: 2`, usage error: `No such option: --party`). Not retried as free-text/party search is unsupported on `fedcourts query`.

## CourtListener MCP Lookups

1. `search(type="o", case_name="MacRae v. Mattos", fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 1 match — *MacRae v. Mattos*, 106 F.4th 122 (1st Cir. 2024) (`cluster_id: 9986857`).
2. `search(type="o", case_name="Hedgepeth v. Britton", fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 1 match — *Jeanne Hedgepeth v. James Britton*, No. 24-1427 (7th Cir. Aug. 26, 2025) (`cluster_id: 10660857`, `opinion_id: 11127444`).
3. `search(type="r", docket_number="24-2908", fields=["caseName", "court", "dateFiled", "docketNumber", "docket_id"])`
   - Result: 62 unrelated district-court/JPML RECAP dockets sharing number `24-2908` (appellate dockets are not in `type="r"`).
4. `search(type="o", court="scotus", case_name="MacRae v. Mattos", fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 0 matches (Justice Thomas's statement respecting denial not indexed under `case_name="MacRae v. Mattos"` on `scotus` opinions).
5. `search(type="o", case_name="Hussey v. City of Cambridge", fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
   - Result: 1 match — *Hussey v. City of Cambridge*, No. 24-1279 (1st Cir. Aug. 15, 2025) (`cluster_id: 10654927`, `docket_id: 68475025`, noting `dateArgued: 2026-04-08`).
6. `search(type="r", court="ilnd", case_name="Inendino v. Nance-Holt", fields=["caseName", "court", "dateFiled", "docketNumber", "docket_id"])`
   - Result: 1 match — *Inendino v. Nance-Holt*, N.D. Ill. No. 1:22-cv-04982 (`docket_id: 65347166`, filed 2022-09-14).
7. `search(type="o", q='"Pickering" "unsupported claims of disruption"')`
   - Result: 0 matches.
8. `call_endpoint(endpoint_id="docket-entries", num_results=20, query={"docket": 65347166, "entry_number": 43, "fields": ["id", "entry_number", "date_filed", "description", "recap_documents"]})`
   - Result: 1 match — First Amended Complaint (N.D. Ill. Dkt. 43, filed 2023-05-31), showing capacities in which defendants were originally named in district court.
9. `search(type="o", citation="606 U.S. 937", fields=["caseName", "court", "dateFiled", "citation", "cluster_id", "opinions"])`
   - Result: 8 unrelated federal decisions matching numbers `606` and `937` across other reporters.
10. `search(type="o", q='"MacRae" "Mattos" "Pickering"')`
    - Result: 4 matches (the First Circuit *MacRae* opinion and three subsequent lower-court opinions citing *MacRae*).
11. `search(type="o", court="ca1", case_name="Hussey v. City of Cambridge", fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "cluster_id"])`
    - Result: 1 match (`cluster_id: 10654927`, 2025-08-15).
12. `search(type="d", court="scotus", party_name="Jorjani")`
    - Result: 0 matches.
13. `search(type="d", court="scotus", party_name="Melton")`
    - Result: 0 matches.
14. `search(type="d", court="scotus", party_name="Schneiter")`
    - Result: 0 matches.
15. `search(type="d", court="scotus", party_name="Darlingh")`
    - Result: 0 matches.
16. `get_endpoint_schema(endpoint_id="clusters")`
    - Result: Returned REST schema for `clusters`.
17. `call_endpoint(endpoint_id="clusters", num_results=10, query={"docket": 68475025, "date_filed": {"lte": "2026-11-16"}, "fields": ["id", "date_filed", "precedential_status", "sub_opinions"]})`
    - Result: 2 clusters on CA1 docket `68475025` (*Hussey v. City of Cambridge*): `10654927` (`2025-08-15` panel opinion) and `10780881` (`2026-01-28` rehearing en banc order), confirming no en banc merits decision had issued as of `2026-11-16`.
18. `read_document(opinion_id=11127444, chunk_index=[0, 3, 4], chunk_size=8000)`
    - Result: Read chunks 0, 3, and 4 (`37,909` total chars) of Seventh Circuit opinion in *Hedgepeth v. Britton*.
19. `search(type="o", court="scotus", q="MacRae Mattos", fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
    - Result: 0 matches.
20. `search(type="d", court="scotus", q="Melton Forrest City", fields=["caseName", "dateFiled", "docketNumber", "docket_id"])`
    - Result: 0 matches.
21. `search(type="d", court="scotus", q="Darlingh", fields=["caseName", "dateFiled", "docketNumber", "docket_id"])`
    - Result: 0 matches.
22. `search(type="o", case_name="Melton v. City of Forrest City", fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
    - Result: Failed with transient HTTP 502 Bad Gateway error from upstream CourtListener.
23. `search(type="o", case_name="Melton v. City of Forrest City", fields=["caseName", "court", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"])`
    - Result: Retry succeeded; 1 match — *Steven Melton v. City of Forrest City, Arkansas*, No. 23-3288 (8th Cir. Aug. 13, 2025) (`cluster_id: 10653052`, `opinion_id: 11119639`).
24. `read_document(opinion_id=11119639)`
    - Result: Read full text (`26,113` chars) of Eighth Circuit opinion in *Melton v. City of Forrest City*.
25. `call_endpoint(endpoint_id="docket-entries", num_results=20, query={"docket": 71381516, "date_filed": {"lte": "2026-11-16"}, "fields": ["id", "entry_number", "date_filed", "description"]})`
    - Result: 0 entries stored on CourtListener for CA7 docket `71381516`.

## Web Searches

- None attempted.
