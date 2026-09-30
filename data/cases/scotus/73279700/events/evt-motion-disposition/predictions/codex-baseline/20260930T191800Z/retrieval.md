# Retrieval log

- Read the provisioned event, context, and November 19, 2025 snapshot. No filed-document directory was present. No other predictor's output or realized outcome was read.
- Consulted repository instructions and prediction, tooling, and flags schemas. Ran `fedcourts paths --court scotus --docket 73279700 --event evt-motion-disposition --role predictor`; the initial `uv run` failed because its default cache was read-only, and the no-sync retry using a temporary cache succeeded. This was path resolution, not a corpus lookup.
- Read the committed `metrics/statpack.md` interim-applications section and inspected top-level metadata keys in `metrics/statpack.json`. Used only application Terms 2015–2024 for the pooled baseline; own-Term and later-Term aggregates were not used as anchors. No `fedcourts query` or `open-events` call was made, and no ranged-corpus transfer line was produced.
- Web search: `site.supremecourt.gov Hollingsworth Perry stay reasonable probability fair prospect irreparable harm 2010`. The tool returned no usable results.
- Attempted to open the official Supreme Court PDF for *Hollingsworth v. Perry*, docket 09A648, at the official opinions/09pdf/09a648.pdf path. The tool returned no usable content.
- CourtListener MCP `search`: type `o`, citation `558 U.S. 183`, one result requested. Returned *Hollingsworth v. Perry*, decided January 13, 2010; lead opinion ID 9413203. Used solely to identify the general stay authority.
- CourtListener MCP `search_document`: opinion ID 9413203, query `reasonable probability`, snippet size 800. Read the standard at 558 U.S. 190. No further opinion material was retrieved.

No search targeted Watkins, application 25A622, Ninth Circuit matter 25-2374, this application's disposition, or its subsequent history. No outcome-revealing material concerning this case was encountered.
