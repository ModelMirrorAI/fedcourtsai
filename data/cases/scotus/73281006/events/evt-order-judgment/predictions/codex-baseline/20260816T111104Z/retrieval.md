# Retrieval

- CourtListener MCP `search` for `Grand v. City of University Heights`, Sixth Circuit opinions filed before June 30, 2026 (query `77b21af6`). It returned the November 13, 2025 opinion, docket 24-3876, opinion ID 11202524.
- CourtListener MCP `read_document` for opinion ID 11202524. I consulted the pre-grant Sixth Circuit opinion's facts and ripeness analysis.
- CourtListener MCP `search` for Supreme Court opinions filed before June 30, 2026 using `"Williamson County" "First Amendment" chilling finality land use` (query `ac96d5f5`). It returned no results.
- Official Supreme Court Question Presented sheet at `https://www.supremecourt.gov/qp/25-00965qp.pdf`, linked by the provisioned snapshot. I retrieved it by HTTPS and extracted the text locally; it supplied the exact granted question.
- Official cert petition at `https://www.supremecourt.gov/DocketPDF/25/25-965/396407/20260217132050131_scan_ajimenez_2026-02-17-12-57-08.pdf`, the URL in `documents.json`. The scanned filing was rendered for visual review because its provisioned text was empty.
- CourtListener MCP opinion search using `type=o`, `court=ca6`, `docket_number=24-3876`, and `filed_before=2026-06-30`, followed by an opinion-metadata lookup for the lower-court panel. These confirmed the published opinion and the Sutton–Batchelder–Larsen panel.
- Attempted SCOTUSblog case-file lookup for *Grand v. City of University Heights*. It returned a 404/home fallback and supplied no substantive information.

No `fedcourts query` corpus lookup was used. The committed `metrics/statpack.md` merits section supplied the base rate.
