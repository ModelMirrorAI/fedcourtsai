# Retrieval beyond the provisioned inputs

No lookup sought this application's Supreme Court disposition, the linked petition's disposition, or subsequent case history. Only the following external and corpus calls were attempted. Local reads of the prompt, schemas, CLI implementation references, project configuration, and working-tree status were operational checks, not additional case evidence.

## Corpus and committed base rates

1. Read `metrics/statpack.md`, specifically the interim-docket caption and per-Term table, and inspected the corresponding `interim.terms` counts in `metrics/statpack.json`. Summed Terms 2007–2016: 9 substantive grants / 107 resolved; 11,175 unparsed applications. Later rows were visible in the common table but were excluded from the anchor.
2. Attempted `uv run fedcourts paths --court scotus --docket 72408073 --event evt-brief-response-disposition --role predictor`. It failed before lookup because the default uv cache path was read-only. Reissued as `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts paths --court scotus --docket 72408073 --event evt-brief-response-disposition --role predictor`; it resolved the intended case and event paths. No installation was attempted.
3. Read query help with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --help`.
4. Queried `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --decided-before 2017 --limit 3`.

   Transfer report: `ranged corpus reads: 274 GET(s), 71827456 byte(s)`.

   Returned three substantive applications: Abraham Moses Fisch v. United States (16A632), Jason Sinagwana Nsinano v. Loretta E. Lynch (16A620), and Michelle Monasky v. Domenico Taglieri (16A557). They illustrate variation in referral and response signals among denied applications. Because the query deliberately conditions on denial, its three denials are not evidence for a denial rate. None is a capital-case matched prior; no opinion bodies were requested or used. The query's pre-2017 mask excluded the target application.

## CourtListener MCP

1. `search(type="o", court="ca5", docket_number="16-70010", filed_before="2017-08-11", num_results=5, order_by="dateFiled desc")`: no results. Did not locate the lower-court opinion.
2. `search(type="o", court="ca5", q='"Long" AND ("Davis" OR "Stephens")', filed_after="2016-01-01", filed_before="2017-08-11", num_results=5, order_by="dateFiled desc")`: 149 matches, with unrelated cases in the first five. Did not hydrate them or infer anything about Long from them. One unrelated hit was dated August 11, 2017; it was not used.
3. `search(type="o", court="ca5", case_name="Long", filed_after="2016-01-01", filed_before="2017-08-10", num_results=10, fields=["caseName", "dateFiled", "docketNumber", "citation", "opinions", "absolute_url"])`: one unrelated 2016 United States v. Long opinion, involving a different person. Not used.
4. `search(type="o", court="scotus", citation="547 U.S. 573", num_results=1, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`: returned Hill v. McDonough, decided June 12, 2006, opinion ID 145647, as general pre-boundary legal context.
5. `search_document(opinion_id=145647, query="stay of execution", snippet_size=900)`: three excerpts, including the discussion at 547 U.S. 583–584 that an execution stay is equitable, not automatic, and must account for the State's enforcement interests. This general principle informed the rationale, not any assumption that Long's legal claim resembles Hill's.
6. `search_document(opinion_id=145647, query="likelihood", snippet_size=650)`: no literal matches. No additional evidence obtained.

No CourtListener REST fallback was attempted.

## Web attempts

The web tool returned no usable content or source references on any of these calls:

1. Search: `site.supremecourt.gov "stay of execution" "reasonable probability" "fair prospect" "2015"`.
2. Search: `Hollingsworth Perry 558 183 2010 opinion 09A648`.
3. Open the official PDF identified by the Hill CourtListener result: `https://www.supremecourt.gov/opinions/05pdf/05-8794.pdf`.

No web material informed the forecast. The general legal context instead came from the CourtListener opinion excerpts and the prediction contract.
