# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. The relevant 2025-Term paid-petition estimated grant rate was 5.36%; the no-CVSG and zero-relist aggregate grant rates were 3.0% and 0.8%, respectively.

## Corpus lookups

- `uv run fedcourts query --court scotus --topic "juvenile life without parole" --limit 5`
  - Failed before any rows or ranged-read statistics were returned because the ranged corpus S3 hostname could not be resolved (`EndpointConnectionError`).
- `uv run fedcourts query --court scotus --citation "Jones v. Mississippi" --limit 5`
  - Failed before any rows or ranged-read statistics were returned for the same DNS reason.

No `ranged corpus reads: ...` line was printed by either failed invocation.

## CourtListener MCP

- Opinion search: `"juvenile" "life without parole" corrigible Jones`, limited to selected relevant courts and filed before 2026-07-17. Returned no results.
- Opinion search: `"transient immaturity" "life without parole"`, filed before 2026-07-17. Returned 512 matches; reviewed the first ten metadata results, including *State of Arizona v. Cooper/Bassett*, *Commonwealth v. Felder*, *State v. Mullins*, *Jones v. Mississippi*, *Walker v. Cromwell*, and *Malvo v. State*.
- Opinion search: `"vacated" "sentence" "final judgment" "1257" resentencing`, filed before 2026-07-17. Returned 88 matches; the first eight metadata results did not materially add to the finality analysis in the BIO.

No web search was used. No search sought this petition's disposition or subsequent history.
