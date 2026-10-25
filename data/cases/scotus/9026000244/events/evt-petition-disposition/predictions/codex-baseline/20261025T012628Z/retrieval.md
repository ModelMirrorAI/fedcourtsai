# Retrieval beyond the provisioned case record

- Read the committed `metrics/statpack.md` modern-cert, circuit, paid-scored relist/CVSG, and salience-band sections; read the corresponding baseline segment fields from `metrics/statpack.json`. Pooled strictly prior Terms 2017–2025: 644 weighted grants / 12,883 weighted resolved = 0.04998835674920438. These are committed-pack values, not a newly refreshed live-corpus query.
- Web search: `site.supremecourt.gov opinions 2025 Laboratory Corporation Davis 24-304 dismissed Kavanaugh uninjured class`. The web tool returned no usable content.
- Web open attempted for the official 2025 Laboratory Corp. slip opinion, identifier `24-304_3e04.pdf`. No usable content was returned. No current-case search was made.
- CourtListener MCP `search`: `type=o`, `case_name=Laboratory Corporation of America Holdings v. Davis`, `court=scotus`, `filed_before=2026-01-01`, `num_results=3`. No results.
- CourtListener MCP `search`: `type=o`, `citation=605 U.S. 327`, `court=scotus`, `num_results=2`. Returned duplicate versions of the June 5, 2025 prior decision, docket 24-304, including opinion 11065594.
- CourtListener MCP `read_document(opinion_id=11065594)`: read the prior Court order and Kavanaugh dissent. Used as primary-source confirmation of earlier review of the class-certification issue and the unresolved legal question. This is not this cell's case or outcome.
- No `fedcourts query` or `open-events` calls; no ranged-corpus transfer lines were generated. No own-case subsequent history or disposition was sought.
