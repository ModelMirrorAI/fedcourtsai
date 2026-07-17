# Retrieval

- Read the committed base-rate context in `metrics/statpack.md` and the Term 2025 paid-petition detail in `metrics/statpack.json`. Relevant rates: modern discretionary-cert petitions approximately 3% granted; Term 2025 paid petitions approximately 5.4% granted; CVSG petitions 27.1% granted. No `fedcourts query` corpus lookup was run, so there is no ranged-corpus-read line.
- Retrieved the United States' May 26, 2026 CVSG brief from the official Supreme Court PDF URL listed in the provisioned snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-113/409896/20260526191106693_Renteria%205.26.26%20post%20proofs.pdf`. The brief recommends holding the petition for *St. Mary Catholic Parish v. Roy*, No. 25-581, and recommends against review of the preemption question.
- Retrieved petitioners' June 9, 2026 supplemental brief from the official Supreme Court PDF URL listed in the provisioned snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-113/412911/20260609105540964_25-113%20Supplemental%20Brief%20and%20Appendix.pdf`. Petitioners request an immediate grant or, alternatively, a hold for *St. Mary*.
- CourtListener MCP opinion search: `case_name="St. Mary Catholic Parish v. Roy"`, `court=ca10`, `filed_before=2026-07-18`, five results requested. It returned no results and did not affect the forecast.
- CourtListener MCP opinion search: `q="\"St. Mary Catholic Parish\""`, `filed_before=2026-07-18`, ten results requested. It returned two irrelevant older opinions and did not affect the forecast.

No search sought this case's disposition or subsequent history.
