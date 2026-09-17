# Retrieval record

## Committed context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-court buckets, relist and CVSG cuts, and the `sal-v4` reached-band table. The numerical anchor uses only displayed Terms 2017–2024. Inspected top-level keys of `metrics/statpack.json`; no case-level material was read from it.
- Ran a local arithmetic check pooling the eight displayed baseline reached rates and denominators. Result: weighted denominator 11,580; approximate pooled percentage 5.1202504317789295. No network or corpus-service read was involved.
- Read the task contract and relevant output schemas. These are instructions, not additional case evidence.

## External attempts

1. Web search: `site.supremecourt.gov Rule 10 considerations governing review certiorari erroneous factual findings misapplication properly stated rule law`. No usable result was returned.
2. Web open: `https://www.supremecourt.gov/ctrules/2023RulesoftheCourt.pdf`. No usable content was returned.
3. Shell fallback: `curl -fsSL --max-time 20 https://www.supremecourt.gov/ctrules/2023RulesoftheCourt.pdf | pdftotext -layout - - | sed -n '/Rule 10\./,/Rule 11\./p' | head -70`. The fetch returned HTTP 404 and `pdftotext` was unavailable. No rules text was obtained or used.

These attempts concerned only general Court rules, not this case or its subsequent history. No CourtListener MCP calls, `fedcourts query`, or `open-events` calls were made. Consequently there are no ranged-corpus transfer lines to report.

## Local operations

`uv run fedcourts paths --court scotus --docket 73272489 --event evt-petition-disposition --role predictor` initially failed because the default cache was read-only. The same command with a temporary cache and `--no-sync` succeeded and identified the case and event paths without exposing an outcome. Local schema/data validation is an output check, not outcome retrieval.
