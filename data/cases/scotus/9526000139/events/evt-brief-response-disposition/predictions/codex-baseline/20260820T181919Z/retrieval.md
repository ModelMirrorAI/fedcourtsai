# Retrieval

No corpus query was used. The committed `metrics/statpack.md` interim-docket section supplied the base-rate context.

CourtListener MCP lookups:

- Searched RECAP for First Circuit docket `26-1774`, limited to filings before 2026-08-04; located *State of California v. Trump*.
- Searched RECAP for First Circuit docket `26-1779`, limited to filings before 2026-08-04; located *State of California v. State of Alabama* and docket ID 73577455.
- Searched District of Massachusetts RECAP records for *State of California v. Trump*, limited to filings before 2026-08-04; located district docket ID 73141063.
- Requested the CourtListener endpoint schema for `docket-entries`.
- Requested the CourtListener endpoint schema for `recap-documents`.
- Listed district-court docket entries filed from 2026-06-01 through 2026-07-31 to identify the appealed orders and supporting documents.
- Searched SCOTUS RECAP records for docket `26A139`, limited to filings before 2026-08-04; no result was returned.
- Listed the district-court docket entries filed on 2026-07-25 and identified RECAP document 487564865, the First Circuit order.
- Read chunks 0–2 of RECAP document 487564865 for the posture, executive-order provisions, district-court injunction, and stay standard.
- Searched RECAP document 487564865 for `intervenor states` to locate the applicants' separate arguments and the majority's treatment of them.
- Searched RECAP document 487564865 for `irreparable` to locate the competing harms analysis.
- Searched RECAP document 487564865 for `partial stay` to locate the dissent's proposed scope of relief.
- Listed First Circuit docket 73577455 entries filed from 2026-07-24 through 2026-07-31 to confirm the 2–1 denial and amicus posture.

No web search was used, and no post-prediction disposition was retrieved.
