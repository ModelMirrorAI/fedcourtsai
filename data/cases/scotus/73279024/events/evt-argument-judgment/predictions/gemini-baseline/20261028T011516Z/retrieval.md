# Retrieval Log

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="ca9", case_name="Prutehi")` — Located the Ninth Circuit decision below, *Prutehi Litekyan: Save Ritidian v. United States Department of the Air Force*, 128 F.4th 1089 (9th Cir. 2025) (`opinion_id: 10799245`).
2. `mcp_courtlistener_read_document(opinion_id=10799245, chunk_index=[0, 1, 2, 3])` — Read the first four chunks of the Ninth Circuit opinion (procedural history and factual background).
3. `mcp_courtlistener_read_document(opinion_id=10799245, chunk_index=[8, 9, 10, 11, 12, 13, 14, 15, 16, 17])` — Read the Ninth Circuit majority's holdings on Article III standing, APA final agency action, and NEPA/RCRA displacement, and the beginning of Judge VanDyke's dissent.
4. `mcp_courtlistener_read_document(opinion_id=10799245, chunk_index=[18, 19, 20, 21, 22])` — Read the remainder of Judge VanDyke's dissent on APA final agency action.
5. `mcp_courtlistener_read_document(opinion_id=10799245, chunk_index=[4, 5, 6, 7])` — Read the Ninth Circuit majority's discussion of standing and *Bennett v. Spear* Prong 1 and Prong 2.

## Corpus CLI Lookups

None (`fedcourts query` / `fedcourts open-events` not used; base rates read from committed `metrics/statpack.md`).

## Web Searches

None.
