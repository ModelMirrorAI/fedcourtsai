# Retrieval record

## Local sources beyond the provisioned record

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Calculated an approximate denominator-weighted baseline reached rate from the displayed 2017–2024 rows; excluded the case's own Term 2025 and later rows from the anchor. No individual case outcomes were retrieved from the corpus.
- Read the task contract and prediction, tooling, and flags schemas. Used `fedcourts paths --court scotus --docket 73500275 --event evt-petition-disposition --role predictor` to resolve paths. The initial invocation failed because the default cache directory was read-only; retrying with a writable temporary cache succeeded.
- No `fedcourts query`, `open-events`, or CourtListener MCP calls. Consequently no ranged-corpus transfer lines were produced.

## General web attempts

The following `web.run` calls returned no usable result text or source identifiers. None supplied evidence or exposed any case outcome.

1. Searches: `site.supremecourt.gov opinions 2023 Macquarie Infrastructure Moab 601 257 pure omissions` and `site.supremecourt.gov Rule 10 considerations governing review certiorari erroneous factual findings`.
2. Searches: `site.supremecourt.gov "Macquarie" "2024" "pure omissions"` and `site.law.cornell.edu rules supremecourt rule_10`.
3. Attempted opening of `https://www.law.cornell.edu/rules/supct/rule_10`.

No search named ON24, Leadersel, this docket number, or the companion case. The prediction uses the supplied pre-decision filings and committed statistical context only.
