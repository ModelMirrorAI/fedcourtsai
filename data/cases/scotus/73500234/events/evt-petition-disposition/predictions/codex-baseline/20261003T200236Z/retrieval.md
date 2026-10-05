# Retrieval record

## Local sources beyond the provisioned inputs

- Read the task contract, repository instructions, and prediction/tooling/flags schemas.
- Read the committed `metrics/statpack.md`: modern-cert disposition and originating-circuit cuts, paid-segment relist and CVSG cuts, and the `sal-v4` per-Term band table. Used `metrics/statpack.json` to pool unrounded baseline reached rates for Terms 2017–2024 only: 593 / 11,580 = 0.0512089810. The pack was not refreshed during this cell.
- Ran `uv run fedcourts paths --court scotus --docket 73500234 --event evt-petition-disposition --role predictor`. The initial invocation failed because the default uv cache was read-only; a rerun with a writable temporary cache succeeded. This resolves paths, not case outcomes.
- No `fedcourts query`, `open-events`, corpus-pull, or CourtListener MCP lookup was performed. Consequently there are no ranged-corpus transfer lines to report.

## Web attempts

These general-context attempts returned empty tool responses, with no usable source text or search results. No present-case query was submitted and no present-case outcome was encountered.

1. Search: `site.supremecourt.gov Rule 10 considerations governing review certiorari erroneous factual findings`.
2. Open the Supreme Court filing-and-rules guidance page at `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
3. Repeat that open after the empty response.
4. Find `Review on a writ` in the attempted official rules PDF URL `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`.

No retrieved web proposition informed the forecast. References to the certiorari standard and litigated precedents rest on the provisioned advocacy, with its limitations stated in `reasoning.md`.
