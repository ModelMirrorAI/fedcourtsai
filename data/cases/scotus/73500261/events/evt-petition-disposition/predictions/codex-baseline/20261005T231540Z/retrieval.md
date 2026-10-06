# Retrieval record

## Committed context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table.
- Read `metrics/statpack.json`: schema keys, timestamp availability, and state-band reached rates and weighted denominators for displayed Terms 2017–2024. Computed their weighted pooled rate, 89/392 = 0.22704081632653061. No individual case rows were retrieved.

## External attempts

1. `web.run` search queries: `site.supremecourt.gov opinions 21pdf Kennedy Bremerton 21-418 history tradition Stone` and `site.supremecourt.gov Rule 10 considerations governing review certiorari judicial discretion`. The tool returned no usable response content or sources.
2. `web.run` open of `https://www.supremecourt.gov/opinions/21pdf/21-418_i425.pdf`, a pre-existing Kennedy opinion source. The tool again returned no usable response content. No text from these attempts informed the forecast.

No CourtListener MCP lookup, corpus `query`, or `open-events` call was made; no ranged-corpus transfer line was produced. No search targeted this petition's disposition or subsequent history, and no companion-case outcome was retrieved.

## Local contract and validation

Read the repository instructions, prediction prompt, and prediction/tooling/flags schemas. Resolved paths with `uv run fedcourts paths --court scotus --docket 73500261 --event evt-petition-disposition --role predictor`. The initial invocation failed because the default uv cache was read-only; retrying with a temporary writable cache succeeded. These operations supplied no external case evidence.

Ran `uv run fedcourts validate data` with the same writable cache after writing the artifacts: **OK: 32956 artifact(s) valid, 44630 reference(s) consistent**. Validation supplied no substantive case evidence.
