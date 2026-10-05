# Retrieval record

## Provisioned inputs

- Read the event definition, `record/context.json`, and `record/snapshots/2026-10-05.json` for this cell only.
- Read `record/documents/documents.json`, the questions presented, and relevant portions of the petition and brief in opposition. The petition is truncated in its appendix; the BIO is not marked truncated. No reply text was provisioned.

## Beyond the provisioned inputs

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, circuit context, paid-segment relist/CVSG cuts, and the `sal-v4` per-Term reached-band table.
- Read aggregate fields of `metrics/statpack.json` to identify the structure and compute the state reached-band anchor for Terms 2017–2025. The exact weighted computation produced 99 grant equivalents over 419 resolved equivalents, or 0.23627684964200477. No case-level corpus lookup was made.
- General-law web search queries: `site.supremecourt.gov Rule 10 considerations governing review certiorari` and `site.supremecourt.gov opinions 2011 Arizona United States 11-182 pdf`. No usable results were returned in this session.
- Attempted web opens of `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf` and `https://www.law.cornell.edu/supremecourt/text/11-182`. Neither returned usable text in this session. Neither informs an independently verified proposition in the prediction.
- No CourtListener MCP calls, no `fedcourts query` or `open-events`, and no ranged corpus reads. No lookup targeted this case's disposition or subsequent history.

## Administrative commands

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction/tooling/flags schemas; checked for scoped instructions.
- Ran `uv run fedcourts paths --court scotus --docket 9026000049 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; retrying with a writable temporary cache succeeded.
- Consulted `fedcourtsai.paths`, `fedcourtsai.ids`, and `fedcourtsai.serialize` to resolve and serialize only the permitted output files. Read the UTC system clock and checked working-tree status without opening unrelated artifacts.
- Validation uses `uv run fedcourts validate data` with the same writable temporary cache; it is an administrative schema check, not a source for the forecast.
