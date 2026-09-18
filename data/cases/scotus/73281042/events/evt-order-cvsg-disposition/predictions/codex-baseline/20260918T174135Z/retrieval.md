# Retrieval record

## Provisioned inputs

Read the cell's event definition, `record/context.json`, `record/snapshots/2026-06-23.json`, and the document manifest, questions-presented extract, petition, and brief in opposition under the case-level `record/documents/`. The petition reading included its attached pre-certiorari appellate decision. No evaluator-only outcome, other predictor's output, or QP-labeling artifact was read.

## Additional local context

- Read the prediction prompt and prediction/tooling/flags schemas.
- Ran `uv run fedcourts paths --court scotus --docket 73281042 --event evt-order-cvsg-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; retrying with a writable temporary cache succeeded. This command resolves paths and performs no case-history retrieval.
- Read `metrics/statpack.md`, specifically the modern discretionary-cert, paid-segment relist/CVSG, and sal-v4 per-Term salience sections. A heading/row search also displayed aggregate rows in other sections; those unrelated aggregates were not used as anchors.
- Inspected `metrics/statpack.json`'s structure and extracted only the sal-v4 high-band reached rates and weighted resolved counts for Terms 2017–2024 for the actual pooling calculation. The total was 314/898 = 0.34966592427616927. Same-Term and later-Term values were not included.
- Read the path and serialization helper interfaces for output preparation.

## Web attempts

The following general-context calls returned no usable result text or source identifiers. They contributed no evidence:

1. Search: `site.supremecourt.gov Rule 10 considerations governing review certiorari`.
2. Search, in the same call: `site.supremecourt.gov Carney Adams 2020 able ready standing 592 U.S. 53`.
3. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
4. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

No search targeted this case, its disposition, subsequent history, or decision coverage. No outcome-revealing search material was returned.

## Corpus and CourtListener

No `fedcourts query` or `open-events` command was used. No ranged corpus transfer line was emitted. No CourtListener MCP lookup was made, and no direct CourtListener REST request was attempted. The committed aggregate statpack and provisioned briefs sufficed for this forecast after the general web attempts yielded nothing.
