# Retrieval

- Consulted `metrics/statpack.md`, "The merits docket (granted cases)," for the strictly prior OT2015-OT2024 merits baseline. No `fedcourts query` command was run and there were no ranged corpus reads.
- Retrieved the official Supreme Court filing linked in the provisioned snapshot: Brief for the United States as Amicus Curiae, filed April 9, 2026, `https://www.supremecourt.gov/DocketPDF/25/25-183/404072/20260409172353690_25-183_Crowther_CVSG.pdf`.
- Retrieved the official Supreme Court filing linked in the provisioned snapshot: Supplemental Brief of Respondents, filed April 23, 2026, `https://www.supremecourt.gov/DocketPDF/25/25-183/405186/20260423142943207_25-183%20Brief.pdf`.
- Retrieved the official Supreme Court filing linked in the provisioned snapshot: Supplemental Brief for Petitioners, filed April 27, 2026, `https://www.supremecourt.gov/DocketPDF/25/25-183/405434/20260427155509185_25-183%20Supplemental%20Brief.pdf`.
- Attempted a CourtListener MCP opinion search for `606 U.S. 357` (*Medina v. Planned Parenthood South Atlantic*). The server returned HTTP 429 because its daily rate limit was exhausted; no search result was used and no REST fallback was attempted.
