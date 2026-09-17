# Retrieval record

## Beyond the provisioned case record

- Read the committed `metrics/statpack.md`: modern discretionary-cert dispositions, originating-court cuts, paid-segment relist and CVSG cuts, and the sal-v4 reached-band Term table. The forecast's anchor uses only the displayed 2017–2024 baseline reached rows. A local arithmetic calculation pooled their rounded rates and denominators; it made no corpus-service request.
- Web search: `site.supremecourt.gov rules Rule 10 writ certiorari compelling reasons erroneous factual findings`.
- Web search, same call: `site.supremecourt.gov "Bowles v. Russell" "equitable"`.
- Web search: `site.supremecourt.gov "Rule 10" "erroneous factual findings"`.
- Web open: official Supreme Court rules PDF at `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.

The web tool returned no usable content for these calls. None supplied facts used in the prediction. No search sought Schmidt's disposition or current docket; no case-specific outcome material surfaced.

## Tooling and contract reads

Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling, and flags schemas. Checked scoped instruction-file locations. Ran `uv run fedcourts paths --court scotus --docket 73363408 --event evt-petition-disposition --role predictor`; the first attempt failed because the default uv cache was read-only, and a retry with a writable temporary cache succeeded. The evaluator-only outcome path was not opened.

No CourtListener MCP lookups and no `fedcourts query` or `open-events` calls were made. There are therefore no ranged-corpus transfer lines to report. Validation is a local artifact check, not case retrieval.
