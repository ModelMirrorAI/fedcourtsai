# Retrieval record

## Provisioned inputs

Read the event definition; `record/context.json`; `record/snapshots/2026-10-05.json`; and `record/documents/documents.json`, `questions-presented.txt`, the petition's question and relevant certworthiness/merits arguments, and the respondents' brief through its conclusion. The petition appendix was not exhaustively reviewed. No outcome file, other predictor output, companion docket, or subsequent case history was read.

## Beyond provisioned inputs

- Read `metrics/statpack.md`: modern cert dispositions, originating-circuit context, paid-segment relist/CVSG cuts, and the sal-v4 per-Term band table. Used `metrics/statpack.json` for exact 2017–2025 federal reached-rate pooling: sum of rate times denominator = 143; sum of denominators = 202; pooled rate = 0.7079207920792079. No 2026 observation entered this anchor.
- General web search attempted: `site.supremecourt.gov 2023 Rules Rule 10 considerations governing review certiorari conflict court appeals`. The tool returned no usable content.
- General official-rules document open attempted: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. The tool returned no usable content. Neither request named this case or sought a case disposition; no external result informed the forecast.

No CourtListener MCP lookup or `fedcourts query`/`open-events` lookup was made. Consequently there are no ranged-corpus transfer lines to report. The committed statpack, rather than a live corpus read, supplied the base-rate context.

## Local contract checks

Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction/tooling/flags schemas. Resolved paths with `uv run fedcourts paths --court scotus --docket 9026000204 --event evt-petition-disposition --role predictor`; the first attempt encountered a read-only default cache and succeeded after selecting a writable cache directory. Local JSON/schema and data validation do not supply case-outcome evidence.
