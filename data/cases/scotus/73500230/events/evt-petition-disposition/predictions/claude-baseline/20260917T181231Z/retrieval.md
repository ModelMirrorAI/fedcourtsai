# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-09-17.json`, `record/documents/documents.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`; `events/evt-petition-disposition/event.yaml`; `metrics/statpack.md` (modern cert by disposition, by originating circuit, relist-count, CVSG, salience-band cuts, per-Term table, and the sal-v4 segment base-rate table).

## Corpus lookups (`fedcourts query`, service backend)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   Returned recent granted SCOTUS rows (mostly substantive applications and unrelated cert grants); no anti-SLAPP analogue. Used only as a sanity check on the corpus surface.
2. `uv run fedcourts query --court scotus --citation '559 U.S. 393' --limit 3`
   stderr: `ranged corpus reads: 1357 GET(s), 355663872 byte(s)` plus a `note:` line that only 200 of 590,919 scotus rows carry citation data. Empty result; the coverage gap, not a missing case.

## CourtListener MCP

1. `search(type=d, court=scotus, q="anti-SLAPP" "Shady Grove")` — failed with HTTP 429 (rate limit exceeded, 300/hour). Not retried; degraded to the filings and the statpack.

## Web fetches (forward cell; documents filed after the provisioned fetch date)

1. Brief in opposition, supremecourt.gov DocketPDF for No. 25-1329 (docket entry Aug 26, 2026). Fetched as PDF; text extracted locally with pypdf and read.
2. Reply brief of petitioners, supremecourt.gov DocketPDF for No. 25-1329 (docket entry Sep 11, 2026). Fetched as PDF; text extracted locally with pypdf and read.

Nothing retrieved concerned this petition's own disposition; the docket stood at "distributed for the September 28, 2026 conference" in every source consulted.
