# Retrieval log

Provisioned inputs read: the event's `event.yaml` and `outcome.json`, `record/context.json`, the 2026-11-19 snapshot, the three staged filings under `record/documents/`, the case summary `summaries/2026-11-19.md`, the three blinded candidate directories, and the interim section of the committed `metrics/statpack.md`.

No corpus query (`fedcourts query` / `open-events`) and no web search.

CourtListener MCP lookups, all to check what gemini-baseline's rationale attributed to the decision below (context for `reasoning_quality` only; not used for any forecast-document grade):

1. `search_document` opinions 11528932 and 11516852, query `3.851`: 6 and 9 matches. 11528932 is Overton v. State (Fla. Nov. 13, 2026); 11516852 is Guardado v. State (Fla. 2026).
2. `search_document` opinions 11528932 and 11516852, query `2013`: 6 and 1 matches, none about a clemency interview.
3. `search_document` opinion 11528932, query `clemency`: 7 matches; part III.B rejects the clemency-process claim on the merits.
4. `search_document` opinions 11528932 and 11516852, query `interview`: 0 and 1 matches (Guardado's interview, July 2026).
5. `search_document` opinion 11528932, query `untimely`: 0 matches.
