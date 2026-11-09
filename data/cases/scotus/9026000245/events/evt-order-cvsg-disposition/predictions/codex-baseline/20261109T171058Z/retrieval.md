# Retrieval record

## Provisioned inputs and local references

Read the prediction contract and prediction schema; the event definition; the November 9, 2026 snapshot; document inventory and questions presented; relevant portions of the petition, opposition, reply, decision below, and appendix; the lower-court docket summary; context; and the empty same-question match list. Read the modern-cert, circuit, paid-segment relist/CVSG/amicus, salience, and prior-Term reached-band sections of `metrics/statpack.md`. These are local references, not a live lookup of this petition's outcome. No evaluations, other predictions, realized outcome file, or QP-topic artifacts were read.

## CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000245 --event evt-order-cvsg-disposition --role predictor` failed before execution because the default uv cache path was read-only. No retrieval occurred. Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000245 --event evt-order-cvsg-disposition --role predictor`; it returned the expected case/event paths and an evaluator-only outcome placeholder, not outcome contents.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. The same help command was subsequently displayed through `head -75` and through `sed -n '72,100p'` to read the structured options without a large terminal response. Help calls do not query corpus cases or print ranged-read counters.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3` succeeded. Returned Goldman Sachs Bank USA v. Brown (25-1408), Scanlan v. Coalition for Open Democracy (26A512, an interim application), and Association for Education Fairness v. Montgomery County Board of Education (26-12). These were generic recent examples, not subject-matter analogues, and received no independent weight in the forecast. The terminal response was truncated, so the first invocation's exact transfer-counter line was not retained in the visible response; I do not invent its values.
4. Repeated the same query with compact display: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 3 | jq -c '{case_id,case_name,docket_number,disposition,cvsg_date,distribution_count}'`. Returned the same three rows. Exact stderr line: `ranged corpus reads: 0 GET(s), 0 byte(s)`. This is the repeated warm-cache call's counter, not a claimed measurement of the first invocation.

No replay clock was set; context identifies a forward cell. No corpus query targeted the subject petition, its subsequent history, or its disposition.

## Web attempts

1. One `web.run` call grouped searches for `site.supremecourt.gov opinions Twitter Taamneh 598 471 2023 conscious culpable`, `site.supremecourt.gov opinions 2025 Smith Wesson Mexico aiding abetting`, and `site.ca2.uscourts.gov Ashley Deutsche Bank 2025 144 F.4th 420`. The tool returned no visible results or source text.
2. A second `web.run` call searched `Twitter v Taamneh Supreme Court 2023 opinion` and `Smith Wesson v Mexico Supreme Court June 5 2025 opinion`. Again no visible results or source text were returned. No fact in the prediction depends on unseen web results. Neither call searched for the subject petition's disposition.

## CourtListener MCP

1. `search(type="o", citation="598 U.S. 471", court="scotus", num_results=2, fields=["caseName","dateFiled","citation","absolute_url","opinions"])`: query `7618134d`; returned two versions of Twitter, Inc. v. Taamneh, decided May 18, 2023, with opinion IDs 10516287 and 9395548 and official Supreme Court PDF references.
2. `search_document(opinion_id=9395548, query="nexus", snippet_size=750)`: returned 12 matches in the Taamneh opinion. Relevant passages reject a universal strict-nexus rule, require assistance to the actionable wrong, and demand stronger culpability as the connection becomes attenuated. Used as general legal context, not as a prediction of this petition's outcome.
3. `search(type="o", court="ca2", citation="144 F.4th 420", num_results=2, fields=["caseName","dateFiled","citation","absolute_url","opinions"])`: query `71f7d860`; zero results. No adverse inference from the absent database match.
4. `search(type="o", court="ca2", case_name="Ashley v. Deutsche Bank", filed_before="2025-12-31", num_results=2, fields=["caseName","dateFiled","citation","absolute_url","opinions"])`: query `aaca1e36`; zero results. Assessment of the claimed split therefore rests on the competing provisioned filings, with that limitation disclosed.

## Validation

The cell is checked with `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000245/events/evt-order-cvsg-disposition/predictions/codex-baseline/20261109T171058Z`. This is local schema/completeness validation, not outcome retrieval.
