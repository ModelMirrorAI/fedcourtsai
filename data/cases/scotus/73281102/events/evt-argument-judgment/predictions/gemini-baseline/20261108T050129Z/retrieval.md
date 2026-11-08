# Retrieval Log

## 1. `fedcourts` CLI Calls

1. `uv run fedcourts paths --court "scotus" --docket "73281102" --event "evt-argument-judgment" --role predictor --predictor "gemini-baseline" --run-id "20261108T050129Z"`
   - Result: Failed with exit code 2 (`No such option: --predictor`).
2. `PREDICTOR_ID=gemini-baseline RUN_ID=20261108T050129Z uv run fedcourts paths --court "scotus" --docket "73281102" --event "evt-argument-judgment" --role predictor`
   - Result: Returned `case_id scotus/73281102`, `corpus corpus/corpus.db`, `event data/cases/scotus/73281102/events/evt-argument-judgment/event.yaml`.
3. `uv run fedcourts query --court scotus --docket-number 25-5930`
   - Transfer line: `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - Result: Returned the corpus row for `scotus/73281102` (*William Maxwell v. Sandra Dinis, Acting Warden*, No. 25-5930).
4. `uv run fedcourts query --court scotus --citation "599 U.S. 465" --citation "605 U.S. 460" --limit 5`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned 0 rows with sparsity note (`note: citations filter: only 200 row(s) in scope (scotus) carry any reporter citation at all...`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `court="ca8"`, `case_name="Osorio-Calderon"`, `fields=["caseName", "dateFiled", "citation", "docketNumber"]`, `num_results=5`)
   - Result: Returned 1 match (`Jose Osorio-Calderon v. Warden FCI Sandstone`, No. 25-3090, filed `2026-06-30`), confirming the Eighth Circuit decision cited in the Solicitor General's merits brief.

## 3. Web Searches

- None.
