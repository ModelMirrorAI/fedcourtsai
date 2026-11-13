# Retrieval record

## Local baseline and reference material

Read the prediction prompt and output schemas; the specified event; record/context.json; record/snapshots/2026-10-02.json; documents.json; questions-presented.txt; supplemental-brief.txt; and relevant substantive sections of petition.txt and appendix.txt. Read the committed metrics/statpack.md, including the prior-Term sal-v8 reached-band table and paid-segment relist, CVSG, and amicus cuts. No other cell's outputs, evaluator outcome, or topic-membership artifacts were read.

Path resolution was first attempted with `uv run fedcourts paths --court scotus --docket 9026000267 --event evt-order-call-for-response-disposition --role predictor`. It failed before lookup because the default uv cache was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache` prefixed. The command named the event and corpus paths and explicitly withheld the evaluator-only outcome path. No packages were installed.

## Corpus calls

Read `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` three times, including wider-column renderings/pipes to expose the options. These were CLI help calls, not corpus transfers.

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026 --limit 4`
   - Rejected: unknown era `modern`. Help explained that era must be a decade token. No transfer line was printed. Corrected in the next call.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4`
   - `ranged corpus reads: 38 GET(s), 9895936 byte(s)`
   - Returned Goldman Sachs Bank USA v. Brown, U.S. DOGE Service v. U.S. District Court, Berry v. United States, and Blanche v. Ozurumba. Distribution counts were 4, 2, 5, and 2. These are unrelated grants, not matched ERISA analogs; I did not use them as a grant-frequency estimate or inspect their documents. Their docket-number Terms precede 2026, although the returned grant dates fall in October/November 2026: the bare-year filter is a Term bar, not a calendar-date bar. This forward cell permits that material, but none drove the forecast.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '552 U.S. 248' --decided-before 2026 --limit 2 --full`
   - `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - No rows. The command warned that only 195 scoped rows carried any reporter citation and recommended CourtListener for a known-case lookup. No opinion body was returned.

## CourtListener MCP

1. `search(type="o", citation="552 U.S. 248", num_results=2, fields=[caseName,citation,dateFiled,absolute_url,opinions])`
   - Returned an unrelated LeVarge result and LaRue v. DeWolff, Boberg & Associates, Inc., decided February 20, 2008; the matching LaRue result included lead opinion 9435269 and combined opinion 145833. Used only the matching case.
2. `search(type="o", court="ca4", case_name="Trauernicht", filed_before="2026-10-02", num_results=3, fields=[caseName,dateFiled,citation,opinions,absolute_url])`
   - One result: Peter Trauernicht v. Genworth Financial Inc., March 10, 2026, No. 24-1880; opinion 11274227. This is the conflicting lower-court precedent, not this petition's own subsequent history.
3. `search_document(opinion_id=11274227, query="appropriate relief", snippet_size=2300)`
   - Five matching excerpts, including slip pages 14–15. Confirmed individualized monetary relief and the mandatory-class-certification context; prospective relief had been dismissed. Relied on this opinion to verify the asserted conflict.
4. `read_document(opinion_id=9435269, chunk_index=1, chunk_size=6500)`
   - Retrieved LaRue's discussion around 552 U.S. 252–255: an individual-account loss can support a plan-based statutory claim. Used as doctrinal context, not as a disposition forecast by another source.

## Web attempts

1. A single web search call submitted two queries: `site.supremecourt.gov opinions LaRue DeWolff 502(a)(2) 2008 552 248` and `site.ca4.uscourts.gov Trauernicht Genworth 502 2026`.
   - The tool returned no usable output or source references. No substantive reliance.
2. Opened the official LaRue opinion PDF at `https://www.supremecourt.gov/opinions/07pdf/06-856.pdf` through the web tool.
   - The tool again returned no usable output. The historical opinion was instead consulted through CourtListener MCP.

Neither web attempt searched for this petition, its disposition, its subsequent history, or anyone else's prediction. No live Supreme Court docket update was attempted.
