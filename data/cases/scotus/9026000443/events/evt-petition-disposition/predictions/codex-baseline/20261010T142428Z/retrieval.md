# Retrieval log

## Local inputs and aggregate context

- Read the cell's event definition, `record/context.json`, `record/snapshots/2026-10-10.json`, and all three provisioned document files: `documents.json`, `questions-presented.txt`, and `petition.txt`.
- Read the governing prompt, repository instructions, prediction and feedback schemas, and the `Prediction` model's field definitions to check the output contract.
- Read `metrics/statpack.md`: modern discretionary-cert disposition and circuit cuts, paid-segment relist and CVSG cuts, and the sal-v4 per-Term reached-band table. Read `metrics/statpack.json` for the exact prior-Term baseline-band counts. No case-level historical outcomes were retrieved.
- Ran `uv run fedcourts paths --court scotus --docket 9026000443 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; the same command succeeded with a writable temporary uv cache. The path resolver withheld the evaluator-only outcome path, and no outcome file was opened.
- Computed the 2017–2025 baseline reached-rate pool locally from the committed JSON: 642 / 12,871 = 0.04987957423665605. No corpus query or open-events command was run, and there are no ranged-corpus-read transfer lines.

## General web retrieval attempts

The following three web-tool calls returned empty responses with no usable source text, snippets, or citations. They contributed no evidence:

1. One search call with two queries: `site.law.cornell.edu rules supremecourt rule 10 certiorari` and `site.uscode.house.gov 29 1055 actuarial equivalent single annuity`.
2. Opened the Supreme Court's general rules-and-guidance page: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
3. Opened the general statutory provision: `https://www.govinfo.gov/link/uscode/29/1055`.

No CourtListener MCP calls were made. No searches sought this case, its disposition, the companion petitions' current status, or post-decision coverage. No outcome-revealing material surfaced.
