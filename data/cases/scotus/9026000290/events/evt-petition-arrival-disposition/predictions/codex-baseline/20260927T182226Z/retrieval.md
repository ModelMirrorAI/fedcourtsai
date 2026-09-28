# Retrieval record

## Local reference material beyond the provisioned inputs

- Read the prediction prompt, repository instructions, and prediction, tooling, and flag schemas to implement the output contract.
- Read `metrics/statpack.md`: modern discretionary-cert disposition table, paid-segment relist and CVSG cuts, and sal-v4 per-Term segment table. Read the corresponding `metrics/statpack.json` fields for exact pooling of the baseline reached rates over displayed Terms 2017-2025. Computed 638 / 12,720 = 0.05015723270440252 with a local Python calculation; no remote corpus read occurred.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify publication provenance: `96ebdd342 2026-09-26T12:03:37Z`. This does not establish the underlying corpus's pull freshness.
- Ran `uv run fedcourts paths --court scotus --docket 9026000290 --event evt-petition-arrival-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; the retry used a writable temporary cache and resolved the event path. No outcome file was read.
- No `fedcourts query`, `open-events`, `stats`, or live corpus lookup was performed. There are no ranged-corpus-transfer lines to report. No CourtListener MCP call was made.

## General web retrieval attempts

The following five calls returned no usable response content. No search result, opinion, rule text, statutory text, or case outcome was obtained or relied upon.

1. Search queries: `site.supremecourt.gov Rule 10 considerations governing review certiorari`; `site.uscode.house.gov 28 USC 1257 final judgments highest court state`.
2. Open attempt: `https://www.supremecourt.gov/filingandrules/2026rulesofthecourt_web.pdf`.
3. Open attempt: `https://www.govinfo.gov/link/uscode/28/1257`.
4. Search queries: `site.supremecourt.gov "Rule 10" "judicial discretion"`; `site.uscode.house.gov "1257" "Final judgments or decrees"`.
5. Repeated open attempt: `https://www.supremecourt.gov/filingandrules/2026rulesofthecourt_web.pdf`.

All queries were about general legal context, not the target case. No target-case search, current docket retrieval, or subsequent-history retrieval was attempted.
