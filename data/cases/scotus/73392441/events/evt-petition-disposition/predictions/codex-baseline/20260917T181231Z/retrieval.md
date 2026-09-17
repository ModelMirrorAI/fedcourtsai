# Retrieval record

## Local context

- Read metrics/statpack.md: modern discretionary-cert disposition counts, paid-segment relist/CVSG cuts, and the sal-v4 reached-band table. A heading/Term-row search also surfaced aggregate interim and merits rows; these did not inform this cert forecast.
- Read the structure and baseline segments of metrics/statpack.json. A jq calculation pooled baseline prefix_est_grant_rate times prefix_weighted_resolved over displayed Terms 2017–2024: 593 / 11,580 = 0.05120898100172712.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json` for artifact vintage: September 14, 2026, commit 55121cdb8. This does not establish corpus refresh timestamps.
- No `fedcourts query` or `open-events` call; no ranged corpus transfer line was generated. No corpus-info lookup was performed.
- Read the task contract and schemas, and the package's paths and serialization interfaces solely to produce the required output. Ran `fedcourts paths --court scotus --docket 73392441 --event evt-petition-disposition --role predictor`. The initial uv invocation failed on a read-only cache; setting `UV_CACHE_DIR=/tmp/uv-cache` allowed it to run.

## General web-tool attempts

All returned empty tool responses, with no usable page or search-result content:

1. Search: `site.supremecourt.gov Rule 10 rarely granted erroneous factual findings misapplication properly stated rule`.
2. Search: `site.constitution.congress.gov Seventh Amendment civil jury trial not incorporated states`.
3. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
4. Search: `site.constitution.congress.gov Seventh Amendment "states"`.
5. Search: `site.supremecourt.gov "2026" "Rules of"`.
6. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

## CourtListener MCP

1. `search(type="o", citation="241 U.S. 211", num_results=1)`: returned Johnson v. Collins, 233 F. Supp. 2d 241 (2002), not the intended authority. Disregarded; no document read.
2. `search(type="o", q="caseName:Bombolis", court="scotus", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])`: found Minneapolis & St. Louis Railroad v. Bombolis, 241 U.S. 211, decided May 22, 1916, opinion 98733.
3. `search_document(opinion_id=98733, query="state courts", snippet_size=600)`: read the excerpts distinguishing Seventh Amendment restrictions on federal proceedings from state-court jury procedure. Used this general precedent, not any history of the predicted case.

## Direct official rules retrieval

- `curl -L --max-time 20 -s https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`: extracted the link identifying the current Court Rules as effective March 16, 2026.
- Attempted `curl -L --max-time 20 -s https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf | pdftotext - -`: extraction failed because pdftotext was unavailable; no text used.
- Attempted an in-memory Python extraction using pymupdf: import failed before a request because the module was unavailable.
- Successfully fetched `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf` in memory with Python urllib.request and pypdf, extracting the pages containing Rule 10. Read printed pages 5–6, including incidental adjacent Rules 9, 11, and the start of 12. Used Rule 10 only.

No search or retrieval sought this petition's disposition, current docket, subsequent history, or post-decision coverage. No files under data/qp-topics were read. No outcome material was encountered.
