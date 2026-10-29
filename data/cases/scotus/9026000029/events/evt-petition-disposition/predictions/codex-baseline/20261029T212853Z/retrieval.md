# Retrieval record

## Provisioned and committed local materials

Read `AGENTS.md`, `.github/prompts/predict.md`, the prediction/tooling/flags
schemas, this event's definition, `record/context.json`, and the October 29,
2026 case-level snapshot. Read the staged questions presented, document
manifest, and relevant petition and appendix sections. No outcome file, other
cell output, or `data/qp-topics/` material was read. A file listing showed the
sibling response-request event; its contents were not read.

Consulted committed `metrics/statpack.md` and the corresponding Term segment
fields of `metrics/statpack.json`. A local `jq` calculation over all displayed
strictly-prior Terms, 2017-2025, gave weighted reached-baseline denominator
12,913, estimated grant-family numerator 660, and rate 0.05111128320297375.
These figures are the committed pack's vintage; no independent build freshness
or corpus-wide polling date was established.

## Corpus commands and environment attempts

1. `uv run fedcourts paths --court scotus --docket 9026000029 --event evt-petition-disposition --role predictor`
   initially failed because uv's default cache was read-only. It was retried
   successfully with `UV_CACHE_DIR=/tmp/uv-cache` and repeated once alongside
   schema inspection; both successful runs resolved this case and event.
2. `uv run fedcourts query --help` initially hit the same cache permission
   error. Retrying with `UV_CACHE_DIR=/tmp/uv-cache` succeeded; a second help
   read with `COLUMNS=160` made the filters easier to inspect.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3`

   ```text
   ranged corpus reads: 12 GET(s), 3145728 byte(s)
   ```

   Returned resolved prior-Term denials with identifiers `scotus/73265705`,
   `scotus/73266074`, and `scotus/73281381`. This was a small filtered service
   check, not a representative rate sample or a close legal analogue search.
   No opinion bodies were requested. The target case was not returned.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info` failed because
   the configured service backend has no client-side connection. It printed
   no corpus-wide vintage and no transfer line. No local blob or alternate
   backend was sought.

## Web attempts

The following calls returned no usable source content to this session. I did
not treat the absence of usable output as evidence about the legal issues:

1. A bundled search with these three queries:
   - `site.supremecourt.gov "Goodyear" "564 U. S. 915" jurisdiction`
   - `site.supremecourt.gov "Bristol-Myers" "general jurisdiction" "specific jurisdiction" "2017"`
   - `site.supremecourt.gov "Cox Broadcasting" "personal jurisdiction" "final"`
2. A bundled search with these two queries:
   - `"Goodyear Dunlop" "Cox" "final"`
   - `site.supremecourt.gov "Rules of this Court" "Rule 10" "erroneous factual"`
3. An attempted open of the Supreme Court's *Bristol-Myers* opinion,
   `supremecourt.gov/opinions/16pdf/16-466_1qm1.pdf`.

No query sought this petition's disposition or later history.

## CourtListener MCP calls

All legal retrieval was through MCP; no direct CourtListener REST fallback
or token access was attempted.

1. `search(type="o", case_name="Daimler AG v. Bauman", citation="571 U.S. 117", num_results=1)`:
   verified the January 14, 2014 opinion, id 2649076. Requested metadata and
   opinion identifiers; the response warned that a requested top-level `id`
   field was absent, while supplying the opinion id inside `opinions`.
2. `search_document(opinion_id=2649076, query="exceptional case", snippet_size=700)`:
   read the exceptional-case limitation in footnote 19. Used for the distinction
   between ordinary operations and being at home.
3. `search(type="o", citation="420 U.S. 469", num_results=1)`:
   the unqualified citation filter returned an irrelevant appellate case,
   *United States v. Eddie Burroughs*, because its parallel citation overlapped
   the numbers. Disregarded; no body read.
4. `search(type="o", court="scotus", case_name="Cox Broadcasting", num_results=1)`:
   correctly returned *Cox Broadcasting Corp. v. Cohn*, March 3, 1975, including
   combined opinion id 109207.
5. `search_document(opinion_id=109207, query="seriously erode", snippet_size=1100)`:
   read the qualified exception to finality despite further state proceedings.
   Used to avoid treating interlocutory posture as an automatic bar.
6. `search(type="o", court="scotus", case_name="Bristol-Myers Squibb Co. v. Superior Court", num_results=1)`:
   returned the June 19, 2017 decision, 582 U.S. 255, including lead opinion
   id 9876893.
7. `search_document(opinion_id=9876893, query="develop", snippet_size=600)`:
   confirmed that the older case lacked forum-based product development and
   marketing-strategy work. Used as a qualification on the petition's proposed
   analogy, not as evidence of what respondents here will argue.

Other local shell inspection concerned path/serialization helpers, schema
structure, and the UTC clock. Those reads did not retrieve case information.
