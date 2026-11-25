# Retrieval Log (`scotus/9026000279`, `evt-petition-disposition`)

## Local CLI / Corpus Queries

1. `uv run fedcourts paths --court "scotus" --docket "9026000279" --event "evt-petition-disposition" --role predictor`
   - Result: Confirmed `case_id = scotus/9026000279`, `event = data/cases/scotus/9026000279/events/evt-petition-disposition/event.yaml`, `DECIDED_BEFORE=<unset>` (forward mode).
2. `uv run fedcourts corpus status` (failed CLI discovery attempt)
   - Result: Exit code 2 (`No such command 'corpus'`).
3. `uv run fedcourts corpus-query --help` (failed CLI discovery attempt)
   - Result: Exit code 2 (`No such command 'corpus-query'`).
4. `uv run fedcourts --help`
   - Result: Listed subcommands (`query`, `stats`, `validate`, `corpus-info`, etc.).
5. `uv run fedcourts corpus-info` (failed on service backend)
   - Result: Raised assertion error because `corpus-info` expects local/ranged file rather than `effective == "service"`, confirming the corpus query sidecar (`service` backend) was active.
6. `uv run fedcourts query --help`
   - Result: Displayed flags for `fedcourts query`.
7. `uv run fedcourts query --court scotus --era 2020s --limit 15`
   - Stats line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned 15 recent 2020s resolved SCOTUS rows (including capital cert denials and interim applications) for schema/prior orientation.
8. `uv run fedcourts query --court scotus --judge Richman --judge Jones --era 2020s --limit 20`
   - Stats line: `ranged corpus reads: 746 GET(s), 195559424 byte(s)`
   - Result: Returned 0 matching SCOTUS rows (SCOTUS rows do not populate lower-court panel judges in `judges`).

*(Committed repository metrics files also read locally: `metrics/statpack.md` and `metrics/amicus-line.json`.)*

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` — `type="o"`, `court="scotus"`, `case_name="McFarland v. Lumpkin"`, `num_results=10`
   - `query_id`: `cc531a5b`
   - Result: `count: 0` (no published SCOTUS opinion/separate writing in *McFarland v. Lumpkin*).
2. `mcp_courtlistener_search` — `type="o"`, `court="scotus"`, `filed_after="2022-01-01"`, `q=""Cronic" AND ("Lumpkin" OR "Guerrero" OR "sleeping" OR "slept")"`, `num_results=15`
   - `query_id`: `75adc6bc`
   - Result: `count: 0`.
3. `mcp_courtlistener_search` — `type="d"`, `court="scotus"`, `case_name="McFarland v. Lumpkin"`, `num_results=5`
   - `query_id`: `10615d88`
   - Result: `count: 0`.
4. `mcp_courtlistener_search` — `type="o"`, `court="scotus"`, `filed_after="2023-01-01"`, `q=""Guerrero" OR "Lumpkin""`, `num_results=15`
   - `query_id`: `c842ecf9`
   - Result: `count: 24` (returned recent SCOTUS opinions citing Texas/habeas decisions including *Rivers v. Guerrero*, 605 U.S. 443 (2025), and *Andrew v. White*, 604 U.S. 86 (2025)).
5. `mcp_courtlistener_search` — `type="o"`, `court="scotus"`, `case_name="Andrew v. White"`, `num_results=3`
   - `query_id`: `c0aa45a0`
   - Result: `count: 2` (returned cluster/opinion metadata for *Andrew v. White*, 604 U.S. 86 (2025), including `opinion_id = 10784605`).
6. `mcp_courtlistener_search` — `type="o"`, `q=""26 F.4th 314" OR "McFarland v. Lumpkin""`, `num_results=10`
   - `query_id`: `32f3bfee`
   - Result: `count: 10` (confirmed *McFarland v. Lumpkin*, 26 F.4th 314 (5th Cir. 2022), and Fifth Circuit decision below in *Alvarez v. Guerrero*, No. 18-70001, filed 2025-12-23, with no SCOTUS opinion reversing *McFarland*).
7. `mcp_courtlistener_read_document` — `opinion_id=10784605`, `chunk_index=[0, 1]`
   - Result: Read opening sections (`total_chars: 78728`, `total_chunks: 10`) of *Andrew v. White*, 604 U.S. 86 (2025) (per curiam).
8. `mcp_courtlistener_read_document` — `opinion_id=10784605`, `chunk_index=[2, 3]`
   - Result: Read reasoning and remand holding of *Andrew v. White*, confirming the Tenth Circuit had refused at the threshold to recognize *Payne*'s due-process rule as clearly established under 28 U.S.C. § 2254(d)(1) without ever reaching whether the state court reasonably applied it, and noting Justice Alito concurred in the judgment and Justices Thomas and Gorsuch dissented.

## Open-Web Searches

None attempted (prohibited by the prediction prompt contract).
