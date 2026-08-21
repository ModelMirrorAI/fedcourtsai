# Retrieval

- CourtListener MCP `search`: RECAP, D.C. Circuit docket `26-5123`, filed before 2026-08-15. Located *National Trust for Historic Preservation v. NPS*, CourtListener docket ID 73204895.
- CourtListener MCP `search`: RECAP party-name search for the National Trust and National Park Service in the D.C. Circuit and District Court, filed before 2026-08-15. Located the underlying D.D.C. docket 1:25-cv-04316 and related records.
- CourtListener MCP `get_endpoint_schema`: inspected the `dockets`, `docket-entries`, and `recap-documents` endpoint schemas.
- CourtListener MCP `call_endpoint`: D.C. Circuit docket entries for docket ID 73204895 through 2026-08-15. Reviewed the pre-application docket history and the August 7 judgment/opinion entries.
- CourtListener MCP `search`: opinions collection for the case filed August 7, 2026; returned no indexed opinion result.
- CourtListener MCP `call_endpoint`: exact August 7, 2026 docket entries for docket ID 73204895. Identified the 2–1 judgment affirming the modified preliminary injunction, the opinion entry, and the mandate schedule.
- CourtListener MCP `call_endpoint`: RECAP documents attached to docket-entry ID 473624176. Located opinion document ID 489096444.
- CourtListener MCP `search_document`: searched RECAP document 489096444 for `statutory authority`, `irreparable harm`, `likelihood of success`, `President's Park`, `Appropriations Clause`, and `National Historic Preservation Act`.
- CourtListener MCP `read_document`: read chunks 0–2 of RECAP document 489096444, covering the panel lineup, the construction and injunction posture, the majority's summary, the governing statutes, and the historical background.
- CourtListener MCP `search_document`: additional searches of RECAP document 489096444 for `preliminary injunction`, `The district court`, `stay pending appeal`, `Executive Order`, `demolition`, and `vacate` to assess the injunction's scope, asserted harms, and procedural posture.
- CourtListener MCP `read_document`: read 20,000-character chunks 0 and 11–16 of RECAP document 489096444, covering the majority's equities analysis and Judge Rao's standing, statutory-authority, and security-equities dissent.
- CourtListener MCP `search`: RECAP, D.D.C. docket `1:25-cv-04316`, filed before 2026-08-15, followed by a docket-entries endpoint lookup through 2026-08-14. The appellate opinion was the more useful synthesis.
- CourtListener MCP `search`: RECAP, Supreme Court docket `26A203`, filed before 2026-08-15; returned no results, so no application text was available there.
- Committed `metrics/statpack.md`: read “The interim docket (applications)” and calculated the strictly-prior OT2026 baseline as 30 grants among 225 resolved substantive applications (13.3%).

No web search or `fedcourts query` corpus lookup was used.
