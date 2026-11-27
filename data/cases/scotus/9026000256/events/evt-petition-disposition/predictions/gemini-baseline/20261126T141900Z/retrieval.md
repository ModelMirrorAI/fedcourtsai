# Retrieval Log (`scotus/9026000256`, `evt-petition-disposition`)

Mode: `forward` (unrestricted pre-decision context; no third-party or project forecasts sought or encountered).

## 1. Corpus queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 25-1360`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: 1 open row (`scotus/73500261`, *Cade Brumley, Superintendent, Louisiana State Education, et al. v. Darcy Roake, et al.*, No. 25-1360, distributed for 2026-12-11, `distribution_count: 3`).
2. `uv run fedcourts query --court scotus --docket-number 26-257`
   - Transfer line: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   - Returned: 1 open row (`scotus/9026000257`, *Mara Nathan, et al. v. Alamo Heights Independent School District, et al.*, No. 26-257, distributed for 2026-12-11, `distribution_count: 1`, 3 amicus counsel entries).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: 10 resolved granted SCOTUS cert rows from the 2020s era (confirming distribution-count and CVSG patterns on recent OT2026 grants).
4. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer line: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Returned: 10 resolved GVR SCOTUS cert rows from the 2020s era.

*(Helper commands also run without corpus transfer: `uv run fedcourts paths --court "scotus" --docket "9026000256" --event "evt-petition-disposition" --role predictor`, `uv run fedcourts query --help`, `uv run fedcourts validate data --help`.)*

## 2. CourtListener MCP lookups

1. `mcp_courtlistener_search(type="o", citation="170 F.4th 292", fields=[...])`
   - Returned: 0 hits (West reporter pagination not yet indexed on the cluster).
2. `mcp_courtlistener_search(type="o", citation="173 F.4th 576", fields=[...])`
   - Returned: 0 hits (West reporter pagination not yet indexed on the cluster).
3. `mcp_courtlistener_search(type="o", q='"Ten Commandments" classroom', filed_after="2025-01-01", fields=[...])`
   - Returned: 6 clusters, including *Roake v. Brumley* panel (`141 F.4th 614`, `cluster_id: 10614580`), *Roake v. Brumley* en banc (`cluster_id: 10797050`, filed 2026-02-20), and *Nathan v. Alamo Heights ISD* en banc (`cluster_id: 10846394`, filed 2026-04-21).
4. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10797050, fields=["id", "case_name", "date_filed", "judges", "sub_opinions"])`
   - Returned: Cluster metadata for *Roake v. Brumley* (`opinion_id: 11263722`).
5. `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10846394, fields=["id", "case_name", "date_filed", "judges", "sub_opinions"])`
   - Returned: Cluster metadata for *Nathan v. Alamo Heights ISD* (`opinion_id: 11313761`).
6. `mcp_courtlistener_search(type="o", q='"Ten Commandments" Arkansas', filed_after="2025-01-01", fields=[...])`
   - Returned: 5 opinion clusters (no Eighth Circuit merits opinion yet on Arkansas Act 573).
7. `mcp_courtlistener_search(type="d", court="ca8", q='"Ten Commandments"', fields=[...])`
   - Returned: 7 Eighth Circuit dockets, identifying pending appeals in *Samantha Stinson v. State of Arkansas* (`25-2713` and `26-1722`) and *Donna Cave v. Cole Jester* (`26-1829`).
8. `mcp_courtlistener_read_document(opinion_id=11263722, chunk_index=[0, 1], chunk_size=8000)` and `mcp_courtlistener_read_document(opinion_id=11263722, chunk_index=[2, 3], chunk_size=8000)`
   - Returned: En banc per curiam opinion and opening of Judge Ho's concurrence in *Roake v. Brumley* (`total_chars: 135177`).
9. `mcp_courtlistener_read_document(opinion_id=11313761, chunk_index=[0, 1, 2], chunk_size=8000)`
   - Returned: Error (`"No text is available for this document."`).
10. `mcp_courtlistener_search(type="o", court="ca5", case_name="Nathan", fields=[...])`
    - Returned: 50 hits; confirmed `cluster_id: 10846394` is the sole Fifth Circuit opinion entry for *Nathan v. Alamo Heights ISD*.
11. `mcp_courtlistener_search(type="o", case_name="Stinson", fields=[...])` and `mcp_courtlistener_search(type="r", court="ca8", case_name="Stinson", fields=[...])`
    - Returned: Confirmed *Samantha Stinson v. State of Arkansas* (`25-2713`, `26-1722`) remains pending in the Eighth Circuit without a published appellate opinion.
12. `mcp_courtlistener_search_document(opinion_id=11263722, query="dissenting", snippet_size=250)` and `mcp_courtlistener_search_document(opinion_id=11263722, query="concurring", snippet_size=250)`
    - Returned: Dissents (Dennis, Haynes, Higginson, Ramirez, joined by Stewart, Graves, Douglas) and concurrence (Ho) in *Roake v. Brumley* en banc.

## 3. Official `supremecourt.gov` docket & filing fetches (`web_fetch`) and web search (`google_web_search`)

1. `web_fetch` of `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1360.html`, `.../26-257.html`, and `.../26-256.html`
   - Returned: Public docket metadata and proceedings entries on all three dockets.
2. `web_fetch` of `https://www.supremecourt.gov/RSS/Cases/JSON/25-1360.json` and `https://www.supremecourt.gov/RSS/Cases/JSON/26-257.json` (two calls: first for proceedings/counsel, second for exact `DocumentUrl` values)
   - Returned: Full current docket proceedings through November 24, 2026 (confirming all three dockets are distributed for the 12/11/2026 Conference) and PDF URLs for companion filings.
3. `google_web_search(query='"Texas Attorney General" election results November 2026')`
   - Returned: Confirmation of the November 3, 2026 election result referenced in Louisiana's BIO (Democrat Nathan Johnson elected Texas Attorney General, 52.4% to 45.9%). No Supreme Court case forecasts surfaced.
4. `web_fetch` of `https://www.supremecourt.gov/DocketPDF/26/26-256/433752/20261124124645615_Dier%2026-256%20-%20Reply%20Brief%20for%20the%20Petitioner.pdf` (two calls: brief overview + detailed section-by-section summary)
   - Returned: Summary of Petitioner Christopher Dier's November 24, 2026 Reply Brief (arguments on *Stone v. Graham*, current classroom implementation, incoming Texas AG adversity issue in *Nathan*, and vehicle comparison with *Brumley* and *Nathan*).
5. `web_fetch` of companion briefs in Nos. `26-257` and `25-1360` (`26-257_Brief in Opposition.pdf`, `26-257 Nathan Cert Reply.pdf`, `25-1360 Brief in Opposition.pdf`, `25-1360 Reply.pdf`)
   - Returned: Summary of QPs, en banc vote alignment, Texas's adversity representation regarding the incoming Texas AG, the *Nathan* petitioners' response that school-district respondents retain independent defense capacity, and both sides' cross-references critiquing *Dier* (`26-256`) as a vehicle.
6. `web_fetch` of `https://www.supremecourt.gov/DocketPDF/26/26-257/420045/20260825123322895_26-%20Corrected%20Petition.pdf`
   - Returned: No extracted text (large combined petition/appendix PDF hit `web_fetch` processing limits).
