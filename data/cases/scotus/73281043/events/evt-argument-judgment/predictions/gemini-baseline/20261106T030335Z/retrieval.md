# Retrieval Log

## Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73281043" --event "evt-argument-judgment" --role predictor`
   - Resolved paths for the cell (`case_id: scotus/73281043`, `corpus: corpus/corpus.db`, `event: data/cases/scotus/73281043/events/evt-argument-judgment/event.yaml`).
2. `uv run fedcourts query --help`
   - Inspected CLI flags for `fedcourts query`.
3. `uv run fedcourts query --court scotus --docket-number 25-1003 --limit 5`
   - `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Returned the corpus metadata row for `scotus/73281043` (*Eric Guerrero, Director, Texas Department of Criminal Justice, Correctional Institutions Division v. Dexter Johnson*, docket `25-1003`, `date_cert_granted: 2026-06-15`, `originating_court: ca5`, `originating_docket_number: 23-70002`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", case_name="Guerrero v. Johnson", fields=["caseName", "dateFiled", "court", "docketNumber", "citation", "absolute_url"])`
   - Returned 4 results, including the Fifth Circuit's January 12, 2026 order denying rehearing en banc (`Guerrero v. Johnson`, No. 23-70002, 164 F.4th 398, `/opinion/7316271/guerrero-v-johnson/`), which is already reproduced in the provisioned petition appendix.

## Web Searches

- None.
