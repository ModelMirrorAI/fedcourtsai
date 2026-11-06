# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 24-935 --decided-before 2026-08-19`
   - `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Returned `scotus/72487215` (*Flowers Foods, Inc., et al. v. Angelo Brock*, No. 24-935): filed 2025-02-28, cert granted 2025-10-20 (`distribution_count: 4`), merits decided 2026-05-28 (`merits_judgment: "affirmed"`).

2. `uv run fedcourts query --court scotus --citation "596 U.S. 450" --citation "601 U.S. 246" --citation "146 S. Ct. 1358" --decided-before 2026-08-19 --limit 10`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (printed coverage note that only 200 SCOTUS rows in scope carry parallel reporter citations).

3. `uv run fedcourts query --court scotus --docket-number 21-1572`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/72470913` (*Domino's Pizza, LLC v. Edmond Carmona*, No. 21-1572): filed 2022-06-17, distributed twice (`distribution_count: 2`), `disposition: "gvr"` on 2022-10-17 (in light of *Southwest Airlines Co. v. Saxon*).

4. `uv run fedcourts query --court scotus --docket-number 23-427`
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/72480005` (*Domino's Pizza, LLC v. Edmond Carmona, et al.*, No. 23-427): filed 2023-10-23, distributed 3 times (`distribution_count: 3`), `disposition: "denied"` on 2024-04-22.

5. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - Returned 5 recent 2020s SCOTUS GVR priors (Nos. 25-1269, 25-1367, 25-7569, 26-139, 26-5216) showing typical `distribution_count` of 1–2 for GVR dispositions.

6. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 recent 2020s SCOTUS denied rows.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Flowers Foods v. Brock"`, `fields=["caseName", "dateFiled", "citation", "docketNumber", "cluster_id", "opinions"]`)
   - Returned 1 result: *Flowers Foods, Inc. v. Brock*, No. 24-935, `cluster_id: 10865526`, `opinion_id: 11332974`, `dateFiled: "2026-05-28"`.

2. `mcp_courtlistener_read_document` (`opinion_id=11332974`)
   - Retrieved the full text (29,837 chars) of the Supreme Court's May 28, 2026 slip opinion in *Flowers Foods, Inc. v. Brock*, No. 24-935 (Gorsuch, J., for a unanimous Court), affirming the Tenth Circuit and holding that a worker who transports goods on an intrastate leg of an interstate journey can qualify for the FAA § 1 exemption without crossing state lines or interacting with vehicles that do.

## Web Searches

- None attempted.
