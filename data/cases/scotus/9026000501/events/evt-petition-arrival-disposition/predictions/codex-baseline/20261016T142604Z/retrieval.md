# Retrieval beyond the provisioned inputs

- Read `metrics/statpack.md`: modern discretionary-cert disposition and circuit cuts, paid-segment relist/CVSG cuts, and the `sal-v4` per-Term segment table. Used only OT2017–OT2025 baseline reached rows for the arrival anchor. Inspected top-level keys of `metrics/statpack.json`; no additional rates were taken from that file. A local Python calculation pooled the displayed rounded percentages, yielding approximately 0.04997344 over weighted n=12,877.
- Web search requests: `site.supremecourt.gov Rule 10 considerations governing review certiorari` and `site.supremecourt.gov opinions Chiaverini City Napoleon 2024 23-50`. The tool returned no visible results; neither request supplied substantive evidence.
- Web open request for `https://www.law.cornell.edu/rules/supct/rule_10`. The tool returned no visible page content; it supplied no substantive evidence.
- CourtListener MCP `search`: type `o`, citation `602 U.S. 556`, two results requested. Returned Chiaverini v. City of Napoleon, decided June 20, 2024, including opinion 11066663 and a revised-slip-opinion result. This lookup concerned a precedent, not the target petition.
- CourtListener MCP `search_document`: opinion 11066663, literal query `We hold`, context size 700; no matches.
- CourtListener MCP `read_document`: opinion 11066663, chunks 0 and 1 at 6,500 characters per chunk. Read the syllabus and opening of the Court's opinion, confirming that the case rejects a categorical bar based on a separate charge supported by probable cause.

No `fedcourts query` or `open-events` lookups were made, so there are no ranged-corpus transfer lines. The path-resolution CLI was used only to identify this event's paths. No target-case outcome or subsequent history was sought or encountered.
