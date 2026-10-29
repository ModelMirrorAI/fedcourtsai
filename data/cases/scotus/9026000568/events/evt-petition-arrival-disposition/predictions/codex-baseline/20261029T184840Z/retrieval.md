# Retrieval record

## Local baseline and reference material

Read the provisioned event, context, snapshot, document manifest, questions
presented, petition body, and selected appended opinion passages. Consulted
AGENTS.md, the prediction prompt, relevant schemas, and metrics/statpack.md
with metrics/statpack.json. The strictly-prior sal-v4 federal risk-set
calculation over the displayed 2017-2025 window was 151/206 = 0.7330097087.
No other cell's prediction or evaluation, realized outcome, or QP-topic
labeling artifact was read.

## Corpus calls

Commands below were run with UV_CACHE_DIR=/tmp/uv-cache after the default
cache proved read-only. The initial `uv run fedcourts paths --court scotus
--docket 9026000568 --event evt-petition-arrival-disposition --role predictor`
and `uv run fedcourts query --help` failed at uv cache initialization, before
retrieval. Both succeeded when repeated with the writable cache. Query help
was also reread in part. The paths command resolved only input/output paths,
not case outcomes.

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 5`
   was executed twice. The first combined terminal output was truncated and
   its transfer line was not retained in the visible excerpt. The repeat
   printed `ranged corpus reads: 0 GET(s), 0 byte(s)`. It returned
   scotus/73281386 (25-1103), scotus/73283862 (25-7026),
   scotus/73500246 (25-1343), scotus/73281619 (25-1131), and
   scotus/73500251 (25-1349). These were general prior grant examples,
   not selected analogues and not a basis for estimating rates. No opinion
   bodies were requested. The year clock is a docket-Term mask, not a
   requirement that the decision predate January 1 of that year.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-104 --limit 1`
   printed `ranged corpus reads: 9 GET(s), 2359296 byte(s)`.
   Returned scotus/9026000104, Rhoney v. Barbosa da Cunha, with a cert grant
   dated October 1, 2026, from the Second Circuit. Used only to corroborate
   the lead grant already described in this petition. No lead merits outcome
   or opinion was requested. This forward-mode companion lookup was not
   subject to a replay clock.

## Web attempts

1. One web search call contained both queries:
   `site.uscode.house.gov 8 USC 1225 b 2 A seeking admission detained`
   and `site.supremecourt.gov Jennings Rodriguez 2018 1225 1226 opinion`.
   The tool returned no usable response content.
2. Open attempted:
   `https://uscode.house.gov/view.xhtml?req=%28title%3A8+section%3A1225+edition%3Aprelim%29`.
   No usable response content.
3. Open attempted:
   `https://uscode.house.gov/us/usc/119-118/t8/s1225/`.
   No usable response content.
4. Open attempted:
   `https://www.govinfo.gov/content/pkg/USCODE-2023-title8/html/USCODE-2023-title8-chap12-subchapII-partIV-sec1225.htm`.
   No usable response content.

No web attempt sought this petition's disposition or subsequent history.
No web-sourced substantive claim entered the forecast.

## CourtListener MCP

One opinion search with `type=o`, `citation=583 U.S. 281`, `num_results=1`,
and fields caseName, citation, dateFiled, absolute_url, cluster_id, opinions
attempted to retrieve Jennings v. Rodriguez. It returned HTTP 429, reporting
the daily limit of 1,400 calls and expected availability in 91 seconds.
No opinion text was returned. No retry or direct REST fallback was made.
