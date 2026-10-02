# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-10-01.json`, `record/context.json`, `record/documents/application.txt` + `documents.json`, the event definition, and the committed `metrics/statpack.md` interim-docket section):

## Corpus (`fedcourts query`, via the cell's corpus service)

1. `uv run fedcourts query --court scotus --include-applications --disposition granted --era 2020s --limit 10`
   stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   Returned mostly time-extension grants (26A438, 26A443, 26A409, 26A429, 26A430, 26A432, 26A433, 26A435) plus two cert rows (25-1131, 25-1349); no substantive stay grants in the ten rows.
2. `uv run fedcourts query --court scotus --include-applications --disposition denied --era 2020s --limit 8`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned eight recent substantive denials (26A370, 26A434, 26A437, 26A382, 26A405, 26A414, 26A415, 26A422), several referred to the Court and denied within one to nine days of filing.

(A first `query` attempt with a free-text argument was rejected by the CLI's usage check and read nothing.)

## CourtListener MCP

3. `call_endpoint` `dockets` with `id=9526000447` — no results.
4. `search` type `d`, court `scotus`, docket_number `26A447` — count 0.

Neither call returned anything about this case; nothing postdating the baseline was seen.

## Web

No web searches.
