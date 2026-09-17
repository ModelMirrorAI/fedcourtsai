# Retrieval record

## Local background

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 reached-band table. A heading/Term-row search also displayed aggregate interim and merits sections; those populations were not used for this cert forecast.
- Read `metrics/statpack.json` structure and baseline-band `prefix_est_grant_rate` and `prefix_weighted_resolved` fields for Terms 2017–2024. Computed the weighted pooled anchor with jq: 593 / 11580 = 0.05120898100172712. Excluded Terms 2025–2026 from the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`: `55121cdb8 2026-09-14T11:02:00Z`. This dates the committed pack, not the remote corpus's newest observation.
- No `fedcourts query` or `open-events` lookup; no ranged-corpus-read line was emitted. No CourtListener MCP lookup.

## General legal context only

1. `web.run` search: `site.supremecourt.gov Rule 10 considerations governing review certiorari erroneous factual findings misapplication properly stated rule law`. Returned no usable tool content.
2. `web.run` open of `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`, attempted twice. Both returned no usable tool content.
3. `curl -fsSL --max-time 30 https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`, filtered to PDF links. Identified the official 2026 Rules PDF.
4. Attempted `curl -fsSL --max-time 30 https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf | pdftotext -layout - -`, with filtering for Rule 10. The extractor was not installed; curl reported a broken output destination. No substantive text was obtained from this attempt.
5. Retrieved that same official PDF with Python `urllib.request.urlopen`, held it in memory, and extracted with installed `pypdf.PdfReader`: first the page containing Rule 10's opening, then in a second request the following page. Read Rule 10 on printed pages 5–6. Adjacent Rules 9, 11, and part of 12 appeared in the extracted pages but do not drive the prediction.

All external requests concerned general Court rules, never this case, its lower-court litigation, or its disposition. No case outcome was surfaced.

## Contract and path checks

Read the repository instructions, prediction prompt, and prediction/tooling/flags schemas. Ran `uv run fedcourts paths --court scotus --docket 73374809 --event evt-petition-disposition --role predictor`; the default cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`. These were administrative checks, not case retrieval. The snapshot and filed-document texts were the provisioned inputs, not external retrieval.
