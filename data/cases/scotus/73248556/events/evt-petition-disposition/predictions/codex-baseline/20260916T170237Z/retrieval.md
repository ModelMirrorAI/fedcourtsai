# Retrieval beyond provisioned case inputs

- Read the committed metrics/statpack.md modern-cert disposition table, paid-segment relist and CVSG cuts, and sal-v4 per-Term segment table. Aggregated only the federal reached rows for 2017–2024 for the scored anchor: approximately 132/181, or 72.9%, reconstructed from rounded published rates. No fedcourts query or open-events call was made; no ranged-corpus transfer line was produced.
- Web search: `site.supremecourt.gov opinions "Hemani" "2026"`. The tool returned no usable content.
- Web open attempt: `https://www.supremecourt.gov/opinions/25pdf/24-1234_new_6k47.pdf`. This was an unverified candidate path; the tool returned no usable content and it supplied no evidence.
- CourtListener MCP search: type `o`, case_name `United States v. Hemani`, court `scotus`, filed_before `2026-09-16`, num_results `3`. It returned one result, cluster 10876933, opinion 11344434, docket 24-1234, filed June 18, 2026, and an official Supreme Court PDF location. Used to corroborate the companion opinion's identity and date only.
- CourtListener MCP search_document: opinion_id `11344434`, query `922(g)(1)`, snippet_size `650`. Returned `No text is available for this document.` No opinion reasoning was obtained.
- Web open of the official PDF location supplied by CourtListener: `https://www.supremecourt.gov/opinions/25pdf/24-1234_g2bh.pdf`. The tool returned no usable content.

No lookup sought Hembree's own Supreme Court disposition, subsequent history, or decision coverage. The characterization of Hemani's substantive holding and the related cert denials comes from the provisioned opposition, with the limitations described in reasoning.md. No live CourtListener REST calls, corpus outcome reads, or labeling-artifact reads were made.
