# Retrieval record

## Provisioned inputs

Read the event definition and case-level context, snapshot `2026-09-15.json`, document manifest, extracted question presented, and selected petition sections including Appendix A. No other prediction, case outcome, or subsequent case history was consulted.

## Beyond provisioned case inputs

- Read committed `metrics/statpack.md`: modern discretionary-cert, paid-segment relist/CVSG, and sal-v4 per-Term salience sections. Inspected committed `metrics/statpack.json` and computed the baseline reached-rate pool for displayed Terms 2017–2025: 638 / 12,720 = 0.05015723270440252. These are aggregate historical context, not a fresh corpus lookup.
- Web search: `site.supremecourt.gov Rule 10 writ certiorari misapplication properly stated rule law`. Tool returned no usable content.
- Web open: `https://www.supremecourt.gov/ctrules/2019RulesoftheCourt.pdf`. Tool returned no usable content.
- Web search: `Supreme Court Rule 10 considerations governing review on certiorari`. Tool returned no usable content.
- Web open: `https://www.supremecourt.gov/filingandrules/2023rulesofthecourt.pdf`. Tool returned no usable content.

No CourtListener MCP calls, `fedcourts query` calls, or `open-events` calls were made; there are no ranged-corpus transfer lines to report. No case-specific web search was made, and no outcome-revealing material surfaced.

## Local contract and tooling

Read repository instructions, prediction prompt and schemas, and path/serialization helpers. Ran `uv run fedcourts paths --court scotus --docket 9026000337 --event evt-petition-arrival-disposition --role predictor`; its first attempt failed because the default uv cache was read-only, then succeeded with the cache redirected to writable temporary storage. Local schema/data validation is an output check, not evidentiary retrieval.
