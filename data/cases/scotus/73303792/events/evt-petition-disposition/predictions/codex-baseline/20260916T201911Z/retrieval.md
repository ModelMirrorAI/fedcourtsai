# Retrieval record

## Local materials beyond the provisioned case inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, and `schemas/agent_tooling.schema.json` for the cell contract.
- Read the modern-cert, circuit, paid-relist, paid-CVSG, and per-Term/salience sections of `metrics/statpack.md`. A headings search also displayed other statistical-section headings and rows, but interim and merits populations were not used as cert anchors.
- Inspected `metrics/statpack.json` keys, coverage, and Term segment fields; used `jq` to pool baseline risk-set numerators and weighted denominators for Terms 2017–2024. Result: 593 / 11,580 = 0.0512089810. No case-level outcome was retrieved from these aggregates.
- Ran `uv run fedcourts paths --court scotus --docket 73303792 --event evt-petition-disposition --role predictor`. The initial attempt failed because the default uv cache was read-only; a retry with a writable temporary cache succeeded. This is path resolution, not a corpus query.
- No `fedcourts query` or `open-events` calls were made. No ranged-corpus transfer lines were produced. No remote corpus freshness claim is made.

## CourtListener MCP

1. `search(type="o", citation="951 F.3d 397", num_results=2)` returned zero results.
2. `search(type="o", q='"VanderKodde"', filed_before="2026-05-01", num_results=3)` returned the 2018 district-court decision, the February 26, 2020 Sixth Circuit decision (opinion 4510506), and a 2023 Rodriguez decision snippet. Only the Sixth Circuit precedent was substantively used.
3. `search_document(opinion_id=4510506, query="source", snippet_size=1200)` returned passages explaining the injury-source test and its application, together with related concurrence excerpts. The forecast relies on the majority's discussion, not the concurrence as circuit law. Source: Sixth Circuit opinion 4510506, slip pp. 5–8; official download identified by the search: `http://www.opn.ca6.uscourts.gov/opinions.pdf/20a0057p-06.pdf`.

## Web attempts

- Search: `site.supremecourt.gov Rule 10 considerations governing review on certiorari erroneous factual findings`.
- Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
- Find on that URL: `A petition for a writ`.

All three web calls returned no usable content in this session. No claim relies on them, and no target-case result surfaced. No target disposition, subsequent history, other predictor output, or labeling-measurement artifact was consulted.
