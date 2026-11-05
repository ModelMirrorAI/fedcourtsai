# Retrieval Log — `gemini-judge` (`scotus/9526000623`, `evt-motion-disposition`, `20261105T213408Z`)

## Corpus Queries (`fedcourts query`)

None — no `fedcourts query` or `fedcourts open-events` calls were made.

## CourtListener MCP Lookups

To verify `gemini-baseline`'s specific citations and factual claims regarding the Florida Supreme Court's decision below (*Guardado v. State*, No. SC2026-1605, decided October 29, 2026), I read the opinion text via CourtListener MCP:

1. `mcp_courtlistener_read_document(opinion_id=11516852, chunk_index=[0, 1], chunk_size=8000)` — verified caption, procedural history, and the three claims raised in Guardado's successive Rule 3.851 motion.
2. `mcp_courtlistener_read_document(opinion_id=11516852, chunk_index=[2, 3, 4], chunk_size=8000)` — verified the Florida Supreme Court's holdings on (A) the *Woodard* executive clemency claim (including footnote 7 noting Guardado's March 2026 notice for a July 2026 clemency interview and the death warrant's certification of clemency review), (B) the untimeliness and procedural bar under Fla. R. Crim. P. 3.851(d) of the penalty-phase and initial-postconviction IAC/mitigation claims (including Dozier School for Boys allegations), (C) the 31-day warrant-period due-process claim, and the 7–0 vote lineup with Justice Tanenbaum's concurring opinion.

## Web Searches

None.
