# Retrieval record

No lookup sought Long's application outcome, its linked petition's disposition, or later own-case proceedings. Local contract/schema/path inspection and provisioned record reads are not external retrieval. The committed metrics/statpack.md interim section was consulted, including the 2007–2016 eligibility window. metrics/statpack.json keys were inspected, not used as an additional source of case facts.

## Corpus and CLI attempts

1. `uv run fedcourts paths --court scotus --docket 72408073 --event evt-motion-disposition --role predictor` failed because uv could not initialize its read-only default cache. No corpus data returned; no ranged-read line.
2. `uv run fedcourts query --help` failed for the same cache reason. No corpus data returned; no ranged-read line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 72408073 --event evt-motion-disposition --role predictor` succeeded and resolved paths without reading an outcome.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` succeeded. A second help invocation, prefixed with `COLUMNS=180` and piped through `sed -n '48,98p'`, inspected filter syntax. Neither performed a corpus lookup or emitted a transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era modern --decided-before 2017 --limit 5` was refused: modern is not an era token. No data or transfer line returned.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era 2010s --decided-before 2017 --limit 5` succeeded, returning five denial-selected priors, including Fisch 16A632, Nsinano 16A620, Monasky 16A557, and Smith 16A545. The result was used only for procedural illustrations, not a grant-frequency calculation. Exact transfer report:

   `ranged corpus reads: 274 GET(s), 71827456 byte(s)`

## Web attempts

1. Search: `site.supremecourt.gov "Hill v. McDonough" "stay" "significant possibility"`. No visible result content returned.
2. Batched searches: `site.supremecourt.gov "Hill v. McDonough" "584"` and `site.supremecourt.gov "Barefoot" "880" "stay" "execution"`. No visible result content returned.
3. Open: `https://www.govinfo.gov/content/pkg/USREPORTS-463/pdf/USREPORTS-463-880.pdf`. No visible result content returned. No claim rests on that attempted fetch.

## CourtListener MCP

1. Opinion search, citation `463 U.S. 880`, limit 1: unexpectedly returned Aranda v. Dal-Tile Corp., a January 11, 2016 order. Not relevant; disregarded.
2. Opinion search, case_name `Barefoot v. Estelle`, court scotus, filed_before `2017-07-31`, limit 2: returned the July 6, 1983 decision, 463 U.S. 880, including opinion 111017, and an April 18, 1983 procedural order. Only the former informed the legal standard.
3. search_document, opinion_id 111017, query `reasonable probability`, snippet_size 1200: returned the passage at pages 895–96 explaining the requirements for a Supreme Court stay of execution. Used as general pre-boundary legal context.
