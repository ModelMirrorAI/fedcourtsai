# Retrieval record

## Local material beyond the provisioned case inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling JSON schemas for the contract. Checked for scoped `AGENTS.md` files without reading other case artifacts.
- Ran `uv run fedcourts paths --court scotus --docket 9526000458 --event evt-brief-response-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; rerunning with its cache directed to `/tmp/uv-cache` succeeded.
- Read the interim section and introductory scope of `metrics/statpack.md`, and the corresponding interim rows in `metrics/statpack.json`. Used a local Python sum to pool substantive grants/resolutions for 2016–2025: 53/549 = 0.0965391621.
- Ran `git log -1 --format='%H %cI' -- metrics/statpack.md` to identify the committed artifact's vintage: `cf9ae960e0a992ca4a051ace24307cf15b9bfb12`, October 13, 2026, 19:17:46 UTC. No live corpus refresh or vintage check was performed.
- No `fedcourts query` or `open-events` calls; consequently there are no ranged-corpus transfer lines to report.

## Web attempts: general precedent only

One search call contained these three queries:

1. `site.supremecourt.gov "West Virginia v. B. P. J." "2026"`
2. `site.supremecourt.gov "Mirabelli" "2026"`
3. `site.supremecourt.gov "injunctive relief" "indisputably clear" "Wisconsin"`

The tool returned no usable output. Following the official PDF location supplied by CourtListener, I made two open attempts and one find attempt (pattern `require`) against Supreme Court opinion PDF `25pdf/24-43_2b35.pdf`; these also returned no usable output. No own-case search was made and no web result informed the prediction.

## CourtListener MCP

1. Opinion search: case name `West Virginia v. B. P. J.`, court `scotus`, filed before `2026-10-14`, three-result limit. Returned the June 30, 2026 decision, docket 24-43, cluster 10882186, opinion 11349709, and its official PDF location.
2. `search_document`: opinion 11349709, literal `do not`, 500-character context. Returned `No text is available for this document.` No REST fallback was used.
3. Opinion search: case name `Mirabelli v. Bonta`, court `scotus`, filed before `2026-10-14`, two-result limit. Returned the March 2, 2026 decision, docket 25A810, opinion 11269328.
4. `read_document`: opinion 11269328, chunk 0, chunk size 13000. Read the opening per curiam portion addressing the parental claims and stay-vacatur posture. This is a different case decided before this application's snapshot.
5. `get_endpoint_item`: opinions item 11349709, fields `id`, `plain_text`, `html`, `html_with_citations`. Returned plain text; the displayed output was truncated. The visible syllabus confirmed B. P. J.'s permissive sex-separated-teams holding; I did not claim to have independently inspected its entire reasoning or footnote reservation.
6. Opinion search: case name `West Virginia v. B. P. J.`, query `"whether" "require"`, court `scotus`, filed before `2026-10-14`, one-result limit. Returned the same opinion with an opening snippet, not the targeted reservation. No additional substantive evidence obtained.

All external retrieval targeted general precedent. No present-case disposition, later docket, outcome file, or labeling-measurement artifact was retrieved.
