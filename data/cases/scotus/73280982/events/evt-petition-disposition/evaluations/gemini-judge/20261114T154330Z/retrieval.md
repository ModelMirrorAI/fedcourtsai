# Retrieval Log (`gemini-judge`, `20261114T154330Z`)

No corpus queries (`fedcourts query`), CourtListener MCP calls, or web searches were made beyond the provisioned inputs and historical statpack verification:

1. `uv run fedcourts paths --court scotus --docket 73280982 --event evt-petition-disposition --role evaluator` — verified resolved case, event, and outcome paths.
2. `uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/<alias>/ --ref origin/main --out-dir ...` (for `gemini-baseline`, `claude-baseline`, and `codex-baseline`) — resolved statpack build `eb6830084a187953fd58b91cb3c9125fc6775a7b` (`sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, `alternative_sha: null`, `sal-v4`) in force at prediction `run_id` `20261026T092709Z` to verify the candidates' cited base-rate figures.
