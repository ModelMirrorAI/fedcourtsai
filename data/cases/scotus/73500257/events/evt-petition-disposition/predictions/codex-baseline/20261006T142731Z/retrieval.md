# Retrieval log

## Committed statistical context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cuts, paid-segment distribution-count and CVSG cuts, and the sal-v4 per-Term band table.
- Read `metrics/statpack.json`: exact baseline-band reached rates and weighted denominators for displayed Terms 2017–2024. Computed the weighted pool as 593 / 11,580 = 0.05120898100172712. No target-case outcome lookup was performed.

## Web attempts

- Search: `site.supremecourt.gov opinions Rivas Villegas Cortesluna 2021 clearly established per curiam`.
- Search: `site.supremecourt.gov opinions Lange California 2021 hot pursuit misdemeanor`.
- Attempted official prior-opinion open: `https://www.supremecourt.gov/opinions/21pdf/20-1539_09m1.pdf`.
- These web calls returned no usable result text or source content. No substantive finding was drawn from them. They targeted general precedent, not this petition's disposition.

## CourtListener MCP

- `search(type="o", case_name="Rivas-Villegas v. Cortesluna", num_results=2)` returned HTTP 429, daily rate limit exceeded. No case content was returned. No REST fallback or credential access was attempted.

## Corpus fallback

Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '595 U.S. 1' --limit 1 --full`.

Transfer report: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.

No rows returned. The CLI reported that only 200 SCOTUS rows in scope carried reporter citations and warned that the empty result was likely a coverage gap. No opinion body was retrieved. The full-body option was confined to one specifically identified prior. No further sparse-filter attempts were made.

## Local task tooling

- Ran `uv run fedcourts paths --court scotus --docket 73500257 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help`; their first attempts failed because the default uv cache was read-only. Both succeeded with `UV_CACHE_DIR=/tmp/uv-cache`.
- Read the task contract, relevant JSON schemas, provisioned inputs, and serialization helper. These are local contract/input inspection, not live case-history retrieval.
- No material revealing this cell's outcome was surfaced.
