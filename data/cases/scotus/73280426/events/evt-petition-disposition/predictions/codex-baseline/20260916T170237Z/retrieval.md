# Retrieval log

## Provisioned inputs

- Read the case-level snapshot `record/snapshots/2026-09-16.json`, `record/context.json`, the event definition, `record/documents/documents.json`, and the questions presented.
- Read substantive portions of `record/documents/petition.txt` and `record/documents/brief-in-opposition.txt`, including the arguments on standing, preservation, racial predominance, Bost, and Callais. These were supplied inputs, not fetched during this cell.

## Additional local context

- Read `metrics/statpack.md`: modern cert disposition population, paid-segment relist and CVSG cuts, and sal-v4 per-Term band table.
- Read selected aggregate fields in `metrics/statpack.json` to calculate the exact elevated reached pool for Terms 2017–2024: 484 / 2,810 = 0.17224199288256228. No case-level corpus query was made.
- Read the task contract, output schemas, and path/serialization helpers solely to produce the required artifacts.
- Ran `uv run fedcourts paths --court scotus --docket 73280426 --event evt-petition-disposition --role predictor`. The default uv cache was read-only; rerunning with a writable temporary cache succeeded. This resolved paths only and returned no outcome material.

## External retrieval attempts

1. Web search batch: `site.supremecourt.gov opinions "Louisiana v. Callais" "2026"` and `site.supremecourt.gov "Bost" "January 14, 2026"`. The tool returned no usable content or source results.
2. CourtListener MCP `search`: `type="o"`, `case_name="Louisiana v. Callais"`, `filed_before="2026-09-17"`, `num_results=3`. Returned HTTP 429; message reported 300/hour exhausted and availability in 172 seconds. No opinion text or search result was received. No retry or direct REST fallback was attempted.
3. Web open of the official rules PDF, `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. The tool returned no usable content. No proposition in the forecast relies on this attempted fetch.

No retrieval targeted this petition's disposition, current docket, subsequent history, or reporting about its resolution. No material from the prohibited labeling-artifact directory was read. No `fedcourts query` or `open-events` call was made, so there is no ranged-corpus transfer line to record. External retrieval added no substantive evidence; the case-specific forecast rests on the supplied record and committed aggregate baseline.
