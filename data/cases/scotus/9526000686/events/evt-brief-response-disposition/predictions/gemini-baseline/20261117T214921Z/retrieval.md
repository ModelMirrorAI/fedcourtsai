# Retrieval Log

## Corpus CLI (`fedcourts`) Lookups

1. `uv run fedcourts paths --court "scotus" --docket "9526000686" --event "evt-brief-response-disposition" --role predictor`
   - Transfer line: *(none — path helper)*
   - Result: Resolved `case_id` (`scotus/9526000686`), `corpus` (`corpus/corpus.db`), and `event` path.

2. `uv run fedcourts query --help`
   - Transfer line: *(none — CLI help)*
   - Result: Listed structured filter flags for `fedcourts query`.

3. `uv run fedcourts query --court scotus --docket-number 26-6154`
   - Transfer line: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Result: Returned 1 row (`scotus/9026006154`, *Thomas M. Overton v. Florida, et al.*), confirming the linked certiorari petition was filed `2026-11-14` from Florida Supreme Court Nos. `SC2026-1724, SC2026-1725` and remains pending (`disposition: null`, `distribution_count: 0`).

4. `uv run fedcourts query --court scotus --docket-number 26-6013`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/9026006013`, *Jesse Guardado v. Florida*, originating from `SC2026-1605`), confirming cert was denied `2026-11-05` with `has_opinion: false`.

5. `uv run fedcourts query --court scotus --docket-number 26-5865`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row (`scotus/9026005865`, *William Reaves v. Florida, et al.*, originating from `SC2026-1512, SC2026-1519`), confirming cert was denied `2026-10-20` with `has_opinion: false`.

6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`
   - Result: Returned 10 recent OT2026 cert denials decided `2026-11-16`.

7. `uv run fedcourts query --court scotus --docket-number 26-78`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 1 row (`scotus/9026000078`, *Michael H. Hunt v. Florida*, filed `2026-07-16`, cited in the Florida Supreme Court opinion below on the nonunanimous-jury habeas issue), still pending (`disposition: null`).

8. `uv run fedcourts query --court scotus --era 2020s --include-applications --limit 30`
   - Transfer line: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - Result: Returned 20 recent OT2026 resolved dockets (`26A690` extension application plus November 16 cert orders).

9. `uv run fedcourts query --court scotus --decided-before 2026-11-06 --limit 10`
   - Transfer line: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Result: Returned 10 rows decided November 3–5, 2026, including Jesse Guardado's two Florida execution stay applications (`26A623` and `26A634`), both resolved `2026-11-05` with `disposition: "denied"`, `interim_reading: "denied"`, `referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`, and `has_opinion: false`.

10. `uv run fedcourts query --court scotus --decided-before 2026-10-21 --limit 10`
    - Transfer line: `ranged corpus reads: 2 GET(s), 524288 byte(s)`
    - Result: Returned 10 rows decided October 19–20, 2026, including William Reaves's Florida execution stay application (`26A524`), resolved `2026-10-20` with `disposition: "denied"`, `interim_reading: "denied"`, `referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`, and `has_opinion: false`.

11. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 15`
    - Transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
    - Result: Returned 15 recent OT2026 granted dockets, including granted substantive applications `26A560`, `26A512`, `26A476`, and `26A428` (*Kenneth Nelsen, Warden v. Christa Gail Pike*, a State warden's application to vacate a stay).

12. `uv run fedcourts query --court scotus --decided-before 2026-10-02 --limit 15`
    - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Result: Returned 15 rows decided September 29–October 1, 2026, including resolved capital stay applications *Curtis W. Beasley v. Florida* (`26A405`, denied, `referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`, `has_opinion: false`) and *Christa Gail Pike v. Tennessee* (`26A414`, denied, `referred_to_court: true`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="fla"`, `case_name="Overton v. State"`, `filed_after="2026-10-01"`, `filed_before="2026-11-17"`, `num_results=5`)
   - Result: 1 match — *Thomas M. Overton v. State of Florida & Thomas M. Overton v. Secretary, Department of Corrections*, `cluster_id: 11061132`, Docket Nos. `SC2026-1724 & SC2026-1725`, filed `2026-11-13` (the decision below).

2. `mcp_courtlistener_search` (`type="o"`, `court="fla"`, `case_name="Guardado v. State"`, `filed_after="2026-09-01"`, `filed_before="2026-11-17"`, `num_results=5`)
   - Result: 1 match — *Jesse Guardado v. State of Florida*, `cluster_id: 11049070`, Docket No. `SC2026-1605`, filed `2026-10-29` (recent Florida Supreme Court precedent cited in Respondent's opposition).

3. `mcp_courtlistener_search` (`type="o"`, `court="ca11"`, `case_name="Barwick"`, `filed_after="2023-01-01"`, `filed_before="2024-01-01"`, `num_results=5`)
   - Result: 1 match — *Darryl Barwick v. Governor of Florida*, `66 F.4th 896`, `cluster_id: 9394630`, filed `2023-05-03` (Eleventh Circuit precedent rejecting *Woodard* due-process challenge to Florida's clemency process).

4. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=11061132`, `fields=["id", "case_name", "date_filed", "judges", "sub_opinions"]`)
   - Result: Returned `opinion_id: 11528932` for *Overton v. State*.

5. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=11049070`, `fields=["id", "case_name", "date_filed", "judges", "sub_opinions"]`)
   - Result: Returned `opinion_id: 11516852` for *Guardado v. State*.

6. `mcp_courtlistener_read_document` (`opinion_id=11528932`, `chunk_index=0`, `chunk_size=12000`)
   - Result: Returned chunk 0 of 3 (`26,614` total chars) of the Florida Supreme Court's November 13, 2026 opinion below in *Overton v. State*.

7. `mcp_courtlistener_read_document` (`opinion_id=11516852`, `chunk_index=0`, `chunk_size=12000`)
   - Result: Returned chunk 0 of 3 (`32,127` total chars) of the Florida Supreme Court's October 29, 2026 opinion in *Guardado v. State*.

8. `mcp_courtlistener_read_document` (`opinion_id=11528932`, `chunk_index=[1, 2]`, `chunk_size=12000`)
   - Result: Returned chunks 1 and 2 of 3 (completing the full opinion below in *Overton v. State*, including the Rule 3.851(d) timeliness bar and alternative *Woodard* merits ruling).

9. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Guardado v. Florida"`, `filed_after="2026-10-01"`, `filed_before="2026-11-17"`, `num_results=5`)
   - Result: 0 matches (confirming no separate opinion was published on the November 5, 2026 stay/cert denials in *Guardado*).

10. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Reaves v. Florida"`, `filed_after="2026-10-01"`, `filed_before="2026-11-17"`, `num_results=5`)
    - Result: 0 matches (confirming no separate opinion was published on the October 20, 2026 stay/cert denials in *Reaves*).

11. `mcp_courtlistener_search` (`type="d"`, `court=["ca11", "flsd", "flmd", "flnd"]`, `party_name="Overton"`, `filed_after="2026-10-01"`, `filed_before="2026-11-18"`, `num_results=5`)
    - Result: 0 matches (confirming no parallel active-warrant federal habeas or § 1983 litigation in Florida federal courts or the Eleventh Circuit).

## Web Searches

- None attempted.
