# Retrieval beyond the provisioned inputs

No retrieval sought this case's disposition, subsequent history, other predictors' outputs, or topic-labeling artifacts.

## Corpus and committed statistical context

- Read the relevant cert sections of metrics/statpack.md and exact segment values in metrics/statpack.json. Pooled the sal-v4 baseline reached rate for the displayed Terms 2017–2025; excluded Term 2026. The pack is committed context, not a newly refreshed corpus. jq verification returned a weighted denominator of 12,913 and grant-family numerator of 660.
- Consulted `uv run fedcourts query --help` twice, once with `COLUMNS=160` and output limited to its first 65 lines. Both help invocations succeeded. All uv commands after the initial paths failure used `UV_CACHE_DIR=/tmp/uv-cache` because the default cache directory is read-only.
- Executed `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --decided-before 2026 --limit 3`. It completed successfully but returned no case rows. Its exact stderr transfer line was:

  `ranged corpus reads: 902 GET(s), 236060672 byte(s)`

  No prior opinion bodies were requested or returned. This empty result is not evidence that the Court never summarily reverses; it is an empty result under the chosen stored-label and time filters. The transfer was substantial, so I made no further corpus query.
- A read-only statistical subagent consulted .claude/agents/stats-reviewer.md and the two statpack files to check pool arithmetic and interpretation of terminal cuts. Its scope expressly excluded case records, outcomes, other cells, browsing, and all edits. I checked the reported aggregate directly before using it.

## General legal context only

1. Web search: `site.supremecourt.gov Heck Humphrey 512 U.S. 477 footnote 6 unreasonable force resisting arrest`. The tool returned no usable search content.
2. Web open: `https://www.govinfo.gov/content/pkg/USREPORTS-512/pdf/USREPORTS-512-477.pdf`. The tool returned no usable document content. No external opinion text was relied on.
3. CourtListener MCP search: `type=o`, `citation=512 U.S. 477`, `court=scotus`, `num_results=1`, requesting caseName, citation, dateFiled, absolute_url, and opinions. Failed with HTTP 429, daily rate-limit exhaustion; the server reported 8,880 seconds until availability. No opinion or case result was returned. I did not attempt a direct REST fallback.

## Local contract and validation utilities

Read AGENTS.md, the prediction prompt, prediction and tooling schemas, and small portions of ids.py, paths.py, serialize.py, and schema definitions solely to resolve paths and validate/serialize this cell. A search for applicable nested AGENTS.md files found none. The first `uv run fedcourts paths --court scotus --docket 9026000094 --event evt-order-call-for-response-disposition --role predictor` failed because the default uv cache was read-only; retrying with the temporary cache succeeded and listed the event path without reading an outcome. These local utilities supplied no additional case evidence.
