# Retrieval log

## Local context beyond the provisioned inputs

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cuts, paid-segment relist and CVSG cuts, salience-band context, and the sal-v4 per-Term risk-set table. Anchoring used only the baseline reached rows for 2017–2025. A heading/Term-row search also displayed other stage sections, which were not used to anchor this cert forecast.
- Inspected only the top-level keys and the type of `terms` in `metrics/statpack.json`; no additional case-level facts were obtained.
- Calculated the denominator-weighted mean of the printed prior-Term baseline reached rates locally: weighted denominator 12,720, approximate probability 0.05010888.
- Read the task instructions and prediction, tooling, and flags schemas for the output contract.
- Ran `uv run fedcourts paths --court scotus --docket 9026000079 --event evt-petition-disposition --role predictor`. The first attempt failed on the default cache's read-only filesystem; retrying with a writable temporary cache succeeded. This resolved paths, not case evidence.

No `fedcourts query` or `open-events` calls were made, so there are no ranged-corpus transfer lines. No CourtListener MCP calls were made.

## Web attempts

All five calls returned no usable response content, search snippets, or readable documents. Nothing from them informed a factual or doctrinal assertion, and none sought this case's disposition.

1. Search: `site.supremecourt.gov Rule 15 brief opposition waiver not granted response requested Rule 10 certiorari`.
2. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
3. Retry the same rules-guidance page.
4. Find `Rule 10.` in the attempted reference `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`.
5. Open that same attempted PDF reference. Its existence and content were not verified.

No case-specific live docket, later history, or outcome was retrieved.
