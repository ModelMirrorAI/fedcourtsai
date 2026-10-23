# Retrieval log

## Committed reference material

- Read the merits-docket section of `metrics/statpack.md` and the matching `merits.terms` rows in `metrics/statpack.json`; computed the strictly prior grant-Term pool, 377/540, from the published rows. Read the merits coverage and baseline cautions in `metrics/README.md`. No live corpus query or open-events lookup was made; consequently there is no ranged-corpus transfer line to report.
- Read task schemas, path/identifier helpers, and serialization helpers to construct and validate the cell output. Ran `fedcourts paths` for this cell; its initial invocation failed on the default uv cache's read-only location, and the invocation with a writable temporary cache succeeded. No evaluator-only outcome file was opened.

## External retrieval attempts

General web searches, none returning usable source content:

1. `site.supremecourt.gov opinions Buck Davis 2017 certificate appealability threshold merits`
2. `site.supremecourt.gov opinions "Jennings" "Stephens" "certificate" 2015`
3. `Buck v Davis 580 U.S. 100 2017 Supreme Court opinion`
4. `site.supremecourt.gov "Current Members" "Jackson"`

CourtListener MCP: `search(type="o", citation="580 U.S. 100", court="scotus", num_results=1)`, seeking Buck v. Davis as general preexisting COA authority. The server returned HTTP 429, a 300/hour limit, with approximately 2178 seconds until availability. No opinion content was returned. I made no direct CourtListener REST request and continued from the provisioned filings.

No search requested Berry's disposition, subsequent history, or a majority opinion in this case. No outcome-revealing material was encountered.
