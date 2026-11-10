# Retrieval Log (`scotus/9526000661`, `evt-motion-disposition`)

## 1. Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000661" --event "evt-motion-disposition" --role predictor`
   - Transfer line: none (`paths` command).
   - Result: Confirmed `case_id: scotus/9526000661` and event path `data/cases/scotus/9526000661/events/evt-motion-disposition/event.yaml`.
2. `uv run fedcourts query --court scotus --docket-number 26-6095`
   - Transfer line: `ranged corpus reads: 737 GET(s), 193069056 byte(s)`
   - Result: No row in corpus for linked certiorari petition `26-6095`.
3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS resolved cert priors (including `scotus/73500384`, *Tauno Waidla v. Christopher Pierce, Warden*, `25-7555`, capital cert denial on `2026-11-09`).
4. `uv run fedcourts query --court scotus --include-applications --limit 15`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 15 recent 2020s SCOTUS resolved priors from warm cache.
5. `uv run fedcourts query --court scotus --docket-number 26A477`
   - Transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned `scotus/9526000477` (*NRCC v. Brown*, `26A477`, substantive application resolved `2026-10-14`).
6. `uv run fedcourts query --court scotus --docket-number 26A500`
   - Transfer line: `ranged corpus reads: 720 GET(s), 188612608 byte(s)`
   - Result: No row for `26A500` in scope.
7. `uv run fedcourts query --court scotus --docket-number 26A400`
   - Transfer line: `ranged corpus reads: 733 GET(s), 192020480 byte(s)`
   - Result: No row for `26A400` in scope.
8. `uv run fedcourts query --court scotus --docket-number 26A300`
   - Transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned `scotus/9526000300` (*Legend Lake Property Owners Ass'n v. Keshena*, `26A300`, extension application).
9. `uv run fedcourts query --court scotus --docket-number 25A1000`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/73281280` (*Michael L. King v. Florida*, `25A1000`, capital substantive stay application denied `2026-03-16`, `referred_to_court: true`, `response_requested: false`).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Pavatt v. Oklahoma")`
   - Result: `0` matches under exact caption `Pavatt v. Oklahoma`.
2. `mcp_courtlistener_search(type="o", q='"Pavatt" "PCD-2026-827" OR "Mark Haydon" OR "Rob Andrew"')`
   - Result: `164` matches, including *Pavatt v. State*, 2007 OK CR 19, 159 P.3d 272 (`cluster_id: 2599359`); *Pavatt v. Carpenter*, 928 F.3d 906 (10th Cir. 2019) (`cluster_id: 4633652`); *Pavatt v. Sharp*, 140 S. Ct. 958 (2020) (`cluster_id: 9365097`); and co-defendant Brenda Andrew's decisions in *Andrew v. White*, 604 U.S. 86 (2025) (`cluster_id: 10318017`) and on remand in the Tenth Circuit (`cluster_id: 10773794`, filed `2026-01-13`).
3. `mcp_courtlistener_search(type="o", q="Pavatt", filed_after="2024-01-01")`
   - Result: `9` matches, including *Andrew v. White* (SCOTUS `2025-01-21` and 10th Cir. `2026-01-13`).
4. `mcp_courtlistener_search(type="r", q="Pavatt", filed_after="2024-01-01")`
   - Result: `9` RECAP dockets, including *Federal Public Defender for the Western District of Oklahoma v. U.S. Department of Justice*, No. `1:26-cv-03731` (D.D.C. filed `2026-10-23`, `docket_id: 75014440`).
5. `mcp_courtlistener_search_document(opinion_id=10773794, query="Pavatt")`
   - Result: `0` matches (confirmed `10773794` was a cluster ID rather than opinion ID).
6. `mcp_courtlistener_search(type="rd", docket_number="1:26-cv-03731")`
   - Result: Listed RECAP documents on `1:26-cv-03731`, including Complaint (`id: 498459355`).
7. `mcp_courtlistener_search(type="o", court="oklacrimapp", q="Pavatt", filed_after="2026-01-01")`
   - Result: `0` published opinions in OCCA matching `Pavatt` after `2026-01-01` (unpublished post-conviction order in `PCD-2026-827` not indexed in CourtListener opinions).
8. `mcp_courtlistener_read_document(recap_document_id=498459355)`
   - Result: Read Complaint in *FPD-WDOK v. DOJ*, No. `1:26-cv-03731` (D.D.C. Oct. 23, 2026), which notes in footnote 2 that James Pavatt is scheduled for execution in Oklahoma on November 12, 2026.
9. `mcp_courtlistener_search(type="r", court=["okwd", "ca10"], q="Pavatt")`
   - Result: `7` RECAP dockets in W.D. Okla. and the Tenth Circuit (*Pavatt v. Royal* / *Pavatt v. Carpenter*, No. `14-6117`; *Andrew v. Tinsley*, No. `15-6190`; *Pavatt v. Jones*, No. `10-6268`).
10. `mcp_courtlistener_read_document(opinion_id=10773794)`
    - Result: Confirmed `opinion_id=10773794` was an unrelated Fourth Circuit opinion because `10773794` was the cluster ID for *Andrew v. White*.
11. `mcp_courtlistener_search_document(opinion_id=4633652, query="shotgun")`
    - Result: `0` matches (because `4633652` was a cluster ID).
12. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=4633652, fields=["id", "case_name", "date_filed", "sub_opinions"])`
    - Result: Resolved *Pavatt v. Carpenter* (10th Cir. 2019 en banc) to `opinion_id: 4410905`.
13. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=2599359, fields=["id", "case_name", "date_filed", "sub_opinions"])`
    - Result: Resolved *Pavatt v. State* (Okla. Crim. App. 2007) to `opinion_id: 9788920`.
14. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10773794, fields=["id", "case_name", "date_filed", "sub_opinions"])`
    - Result: Resolved *Andrew v. White* (10th Cir. Jan. 13, 2026 remand opinion) to `opinion_id: 11240379`.
15. `mcp_courtlistener_search_document(opinion_id=11240379, query="Pavatt")`
    - Result: `46` matches in *Andrew v. White* (10th Cir. Jan. 13, 2026) detailing the trial record of the 2001 murder of Rob Andrew, the 16-gauge shotgun shells, and the Tenth Circuit's affirmance on remand.
16. `mcp_courtlistener_search_document(opinion_id=4410905, query="shotgun")`
    - Result: `25` matches in *Pavatt v. Carpenter*, 928 F.3d 906 (10th Cir. 2019) (en banc), detailing the 16-gauge shotgun evidence, the two shotgun blasts, and the en banc Tenth Circuit's rejection of Pavatt's habeas challenges.
17. `mcp_courtlistener_search(type="o", court="oklacrimapp", filed_after="2026-01-01")`
    - Result: `21` published OCCA opinions in 2026 (confirming unpublished orders in capital post-conviction dockets `PCD-YYYY-NNN` are not published to the `oklacrimapp` opinion feed).
