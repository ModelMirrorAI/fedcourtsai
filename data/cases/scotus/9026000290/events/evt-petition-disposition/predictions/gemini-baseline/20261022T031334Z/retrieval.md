# Retrieval Log

## 1. Corpus Tooling (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9026000290" --event "evt-petition-disposition" --role predictor`
   - Output: resolved `case_id` (`scotus/9026000290`), `corpus` (`corpus/corpus.db`), and `event` (`data/cases/scotus/9026000290/events/evt-petition-disposition/event.yaml`).
2. `uv run fedcourts query --court scotus --era 2020s "Emberton"`
   - Output: CLI usage error (rejected free-text positional argument; no ranged reads).
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer line: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
   - Purpose: Inspected recent 2020s SCOTUS denied priors in the corpus.

## 2. CourtListener MCP Server Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Emberton v. San Francisco"`, `num_results=10`)
   - Result: 0 published opinions matching that caption.
2. `mcp_courtlistener_search` (`type="r"`, `docket_number="22-cv-05440"`, `num_results=10`)
   - Result: Located `Emberton v. San Francisco City Government`, Docket ID `65372718` (`3:22-cv-05440`), U.S. District Court for the Northern District of California (filed 2022-09-23, terminated 2023-07-21).
3. `mcp_courtlistener_search` (`type="r"`, `party_name="Emberton"`)
   - Result: Confirmed `Emberton v. San Francisco City Government` (`docket_id=65372718`) as the sole federal docket involving petitioner Mihal Emberton.
4. `mcp_courtlistener_search` (`type="o"`, `q=""Emberton" "San Francisco""`)
   - Result: 6 unrelated opinions; confirmed no published appellate opinion in petitioner's state or federal litigation.
5. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="dockets"`, `item_id=65372718`)
   - Result: Retrieved docket metadata for `Emberton v. San Francisco City Government` (N.D. Cal. No. 3:22-cv-05440-TSH, removed under 28 U.S.C. § 1441, terminated July 21, 2023).
6. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=65372718`, `num_results=20`)
   - Result: Listed docket entries through entry #40, including Order Granting Motion to Dismiss (ECF No. 35, entry ID `346406411`, filed 2023-06-13) and Order Striking Federal Claims and Remanding State Law Claims (ECF No. 37, entry ID `359437867`, filed 2023-07-21).
7. `mcp_courtlistener_call_endpoint` (`endpoint_id="recap-documents"`, `docket_entry=359437867`) & (`docket_entry=346406411`)
   - Result: Resolved RECAP document IDs `366028310` (ECF No. 37) and `352783335` (ECF No. 35).
8. `mcp_courtlistener_read_document` (`recap_document_id=366028310`) & (`recap_document_id=352783335`)
   - Result: Read full text of Judge Thomas S. Hixson's June 13, 2023 Order (dismissing § 1983 claims under *Younger v. Harris*, dismissing RICO claims with prejudice, and denying motion to disqualify City Attorney) and July 21, 2023 Order (striking unauthorized federal claims in the Third Amended Complaint and remanding state-law claims to San Francisco Superior Court).
9. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=65372718`, `entry_number=19`) & (`endpoint_id="recap-documents"`, `docket_entry=219512564`)
   - Result: Resolved RECAP document ID `225594146` (ECF No. 19, filed 2023-02-15).
10. `mcp_courtlistener_read_document` (`recap_document_id=225594146`)
    - Result: Read full text of Judge Hixson's February 15, 2023 Order on Motion for Judgment on the Pleadings (analyzing and rejecting petitioner's Fourth Amendment search/seizure claims, Fourteenth Amendment Equal Protection and Due Process claims, Title II claim, 31 U.S.C. § 6711(a) claim, ICCPR claim, and 18 U.S.C. § 242 claim).

## 3. Web Searches

- None performed.
