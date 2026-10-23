# Retrieval

## Provisioned case inputs

Read the September 15, 2026 snapshot and context, event definition, document manifest, questions presented, SG invited brief, and relevant portions of the petition, combined briefs in opposition, and cert reply. No current case docket, Supreme Court disposition, subsequent history, other cell output, or topic-label artifact was retrieved.

## Aggregate context

Consulted committed `metrics/statpack.md` and `metrics/statpack.json`: modern discretionary-cert population, originating-circuit cut, paid-segment relist and CVSG cuts, and the sal-v4 prior-Term high-band risk sets. JSON arithmetic pooled OT2017–OT2024 high-band reached rates with their weighted resolved denominators: 314/898. The CVSG cut supplies 57 grant-family outcomes among 164 resolved petitions. No live corpus query or `open-events` call was made, so there is no ranged-corpus transfer line. These are the available committed pack's figures; its corpus freshness was not independently verified.

## External research, in order

1. Web search: `site.supremecourt.gov opinions 2021 United States Washington 21-404 intergovernmental immunity 2022 Goodyear Atomic`. The tool returned no usable content.
2. Attempted web open of the Supreme Court opinion URL ending in `21-404_i3dj.pdf`. The tool returned no usable content; nothing from it informed the prediction.
3. CourtListener MCP `search(type="o", case_name="United States v. Washington", citation="596 U.S. 832", num_results=3)`: located the June 21, 2022 decision, opinion ID 6351405, docket 21-404. This is general precedent, not this cell's petition.
4. CourtListener MCP `search_document(opinion_id=6351405, query="discriminat", snippet_size=650)`: inspected excerpts about protection of federal contractors against discriminatory state laws.
5. CourtListener MCP `read_document(opinion_id=6351405, chunk_index=[2,3], chunk_size=5000)`, then `read_document(opinion_id=6351405, chunk_index=4, chunk_size=5000)`: checked the opinion's background and the distinction between discrimination/direct regulation and neutral indirect costs. Used that distinction as legal context, not as an outcome prediction supplied by the source.
6. CourtListener MCP `search(type="o", citation="145 F.4th 315", num_results=1)`: returned zero results. No opinion was retrieved. I used only the provisioned parties' and SG's competing characterizations of CoreCivic and did not interpret the empty lookup as evidence against its existence.

Operational reads of the instructions, schemas, path helper, and serialization helper supported artifact production, not additional case research. The initial path-resolution command encountered a read-only default uv cache; rerunning with a temporary cache succeeded.
