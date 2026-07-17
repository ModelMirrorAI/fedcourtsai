# Retrieval

- Read `metrics/statpack.md`, especially the modern discretionary-cert disposition, relist, CVSG, originating-circuit, and per-Term sections. No ranged corpus read was involved.
- CourtListener MCP opinion search: `q="Richard Devillier Texas takings mandamus"`, opinion collection, 10 results. This identified the prior Fifth Circuit litigation.
- CourtListener MCP opinion search: `case_name="Devillier v. Texas"`, `court="scotus"`, filed during 2024. This identified *DeVillier v. Texas*, 601 U.S. 285 (2024), CourtListener cluster 9493901/opinion 9960514.
- CourtListener MCP opinion endpoint lookup: opinion 9960514, limited to the consolidated opinion text. Consulted the unanimous 2024 opinion and mandate language.
- Direct document retrieval from the Supreme Court petition URL contained in the provisioned snapshot: `20260501162835028_25-%20Petition.pdf`. Consulted the question presented, procedural history, Rule 20 argument, mandate-enforcement argument, and requested relief. I did not search for the petition's disposition.
- CourtListener MCP opinion search: `citation="132 F.4th 746"` (no result), followed by `case_name="Devillier v. State of Texas"`, `court="ca5"`, filed September 2024 through April 2025. Consulted the September 26, 2024 Fifth Circuit order at cluster 10125529/opinion 10592130.
- CourtListener MCP opinion endpoint lookup: opinion 10592130, limited to the consolidated opinion text.
- CourtListener MCP opinion search: `q="\"132 F.4th 746\" OR \"remand to the District Court\" \"Devillier\""`, `court="ca5"`. This confirmed the related Fifth Circuit opinion history; the petition itself supplied the later order's relevant text.

No `fedcourts query` or `fedcourts open-events` lookup was used.
