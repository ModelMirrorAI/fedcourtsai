# Retrieval

- Consulted `metrics/statpack.md` and `metrics/statpack.json` for the modern-cert, Ninth Circuit, relist, CVSG, and `sal-v3` prior-Term arrival anchors. This was committed base-rate context, not a live corpus query.
- CourtListener MCP RECAP search for `"Randy Quaid" "Craig Granet"` in the Ninth Circuit, first for basic case metadata and then for docket identifiers and available documents. It identified consolidated appeals 25-270 and 25-1026 and surfaced pre-petition orders.
- CourtListener MCP docket endpoint schema lookup, used to restrict subsequent endpoint fields.
- CourtListener MCP docket-entry lookup for Ninth Circuit docket 69660612. It showed consolidation, counsel withdrawal, pro se status, and denial of an emergency injunction motion.
- CourtListener MCP opinion search for `Quaid v. Granet` in the Ninth Circuit, limited to filings before 2026-08-27. It returned no results.
- CourtListener MCP RECAP search for district docket `2:24-cv-03455`. It identified C.D. Cal. docket 68477124 and the nature of suit.
- CourtListener MCP docket-entry lookup for district docket 68477124. It showed the dismissal, vexatious-litigant and prefiling rulings, fee award, and later appellate memorandum entries.
- CourtListener MCP lookup for district docket entry 160 (the May 2026 Ninth Circuit memorandum). The linked RECAP document 479446012 was unavailable and contained no readable text.

No `fedcourts query` or `open-events` corpus lookup was used, so there are no ranged-corpus-read lines.
