# Retrieval record

## Provisioned inputs and local reference material

Read the prediction prompt and output schemas, the target event definition, `record/context.json`, `record/snapshots/2026-10-21.json`, `record/documents/documents.json`, and the whitespace-only `record/documents/application.txt`. Local file discovery listed paths only; it did not read case outcomes, prediction outputs from other cells, or labeling-measurement artifacts.

Read the interim section of `metrics/statpack.md` and inspected `metrics/statpack.json` with `jq`. The required 2016–2025 finer-reading pool totals zero grants, zero resolved, and 1,366 unread resolutions, so it supplies no baseline. No corpus query or open-events call was made; there was no ranged-corpus-reads stderr line.

Administrative command `uv run fedcourts paths --court scotus --docket 9526000612 --event evt-motion-disposition --role predictor` initially failed because the default uv cache was read-only. Retrying with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and identified the target event path. No package installation was attempted. Validation uses the same cache override.

## Web attempts

All three `web.run` calls below returned no usable result text, source, or document content. None informed the substantive forecast.

1. Opened the official historical rules PDF at `https://www.supremecourt.gov/ctrules/2019RulesoftheCourt.pdf` for general procedural context. No rules were retrieved or relied on as current authority.
2. Searched `site.supremecourt.gov rules injunction application Rule 23 2026` for current official procedural context. No usable results returned.
3. Opened the application PDF URL supplied by `documents.json`: `https://www.supremecourt.gov/DocketPDF/26/26A612/431265/20261030114918676_26A612.pdf`. No usable PDF content returned. This targeted the filed application, not a disposition or docket history.

## CourtListener MCP attempts

1. `search(type="o", court="cadc", docket_number="26-5131", filed_before="2026-10-21", num_results=5)` — query `09b62523`, count 0, empty results. Sought a pre-cutoff lower-court opinion only.
2. `search(type="d", court="cadc", docket_number="26-5131", case_name="Akerman", filed_before="2026-10-21", num_results=5)` — query `c491cfc7`, count 0, empty results. Sought the lower-court docket only. No docket or subsequent entry was retrieved.

No REST fallback, case-outcome search, live Supreme Court docket lookup, or post-decision coverage retrieval was attempted. No outcome-revealing material was encountered.
