# Retrieval log

## Local contract and baseline

Read `.github/prompts/predict.md`, the prediction and tooling/flags schemas, the event definition, `record/context.json`, `record/snapshots/2026-11-15.json`, the document manifest, questions presented, relevant petition sections and appendix passages, the separate decision below, and the limited lower-court-docket extract. Consulted `metrics/statpack.md`, especially modern-cert dispositions, the paid-segment relist/CVSG/amicus cuts, and prior-Term `sal-v8` reached rates. No predictions or evaluations belonging to another cell were consulted.

An initial `uv run fedcourts paths --court scotus --docket 9026000446 --event evt-petition-disposition --role predictor` failed because the default uv cache was read-only. Reissuing with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and confirmed the case/event paths. No packages were installed. Read `uv run fedcourts query --help` with that cache override, including narrower reformatted views of its output. Consulted the corpus-client timeout declarations after a query remained pending; no alternative CourtListener transport or credentials were sought.

## Corpus lookups

All queries used `UV_CACHE_DIR=/tmp/uv-cache`. The context is forward mode with no replay clock.

1. `uv run fedcourts query --court scotus --topic 'Civil Rights' --era 2020s --limit 5`
   - Returned no rows. Warning: none of the 592,082 SCOTUS rows in scope carried topic metadata; the exact topic field is populated on circuit rows instead. This was a metadata gap, not evidence of no comparable cases.
   - `ranged corpus reads: 2321 GET(s), 607977472 byte(s)`
2. `uv run fedcourts query --court scotus --citation '605 U.S. 303' --limit 1`
   - Attempted to identify *Ames* as contextual precedent. Returned no rows. Warning: only 195 SCOTUS rows carried reporter citations; this filter searches a case's own citations, not citations in its text. No conclusion about the existence or content of *Ames* was drawn from the empty result.
   - `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 3`
   - Returned *James Dwight Pavatt v. Oklahoma*, No. 26-6095 (cert denied November 12, 2026), its separate substantive application No. 26A661 (denied the same day), and *Paul Schultz v. H. Jason Gold*, No. 26A658 (substantive application denied November 11, 2026). None concerns this petition. They are poor employment-discrimination comparators, and two are interim applications, which this CLI includes even without `--include-applications`. Because the query selects denials, its results cannot estimate a grant rate. No numerical adjustment rests on these rows.
   - `ranged corpus reads: 1 GET(s), 262144 byte(s)`

## CourtListener MCP calls

1. `search(type="o", case_name="McCreight v. AuburnBank", num_results=3)` — no matches for that case-name spelling.
2. `search(type="o", citation="117 F.4th 1322", num_results=2)` — found *Julia McCreight v. Auburn Bank*, Eleventh Circuit, September 19, 2024; cluster 10121857, opinion 10588458. Used the court's opinion, not forecasts or later case commentary.
3. `search_document(opinion_id=10588458, query="specifically raised", snippet_size=1000)` — one match. Read the preservation requirement in footnote 6 and the surrounding distinction between a claim and its legal theory.
4. `search_document(opinion_id=10588458, query="not enough", snippet_size=750)` — returned nine matches, including the explanation that citing a mixed-motive decision did not suffice where the plaintiff argued only pretext. Other snippets concern evidentiary insufficiency; they do not establish the merits of Tarquinii's separate record.
5. `search(type="o", citation="96 F.4th 566", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])` — found *Bart v. Golub Corp.*, Second Circuit, March 26, 2024; opinion 9954482.
6. `search_document(opinion_id=9954482, query="irrelevant", snippet_size=750)` — two matches. The relevant footnote describes single-/mixed-motive differences as irrelevant at summary judgment, supporting but not conclusively establishing the petition's precise preservation conflict.

## Web calls

1. One `search_query` call attempted both `site.ca11.uscourts.gov McCreight AuburnBank 117 F.4th 1322 mixed motive 2024` and `site.ca2.uscourts.gov Bart Golub 96 F.4th 566 2024 mixed motives`. No usable results or snippets were visible in the tool response.
2. One `open` call attempted the official Eleventh Circuit opinion at `https://media.ca11.uscourts.gov/opinions/pub/files/202212577.pdf`. No usable content was visible in the tool response. The substantive check instead used the opinion text supplied through CourtListener MCP.

No search sought this petition's own disposition, subsequent history, or anyone else's forecast. No outcome-revealing material or external forecast of this petition surfaced. No live Supreme Court docket refresh was attempted.
