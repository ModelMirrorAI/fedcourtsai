# Retrieval record

## Provisioned and local inputs

- Read AGENTS.md, .github/prompts/predict.md, and the prediction, flags, and tooling schemas. Inspected local path/serialization helper definitions to understand output handling.
- Read this cell's event.yaml, record/context.json, record/snapshots/2026-09-17.json, record/documents/documents.json, questions-presented.txt, and relevant petition.txt sections. No other prediction, evaluation, or realized-outcome file was consulted.
- Read metrics/statpack.md: modern-cert counts, paid-segment relist/CVSG cuts, originating-court context, and the sal-v4 reached-band table. Checked metrics/statpack.json top-level metadata keys for a build/freshness timestamp; none of the checked timestamp keys was present. Pooled displayed baseline reached rates for Terms 2017-2024 locally: denominator 11,580, weighted rounded-table rate 0.0512025043.
- Ran `uv run fedcourts paths --court scotus --docket 73500231 --event evt-petition-disposition --role predictor`. The default cache was read-only; reran successfully with `UV_CACHE_DIR=/tmp/uv-cache`. This resolves paths, not corpus facts.
- No `fedcourts query` or `open-events` call; no ranged-corpus transfer line was produced.

## General web attempts

These calls returned no visible search results or page content and supplied no substantive evidence. None named the target petitioner or sought the target disposition.

1. Search: `Lawlor National Screen Service 349 U.S. 322 1955 judgment without findings precludes same cause`.
2. Same call, second search: `site.supremecourt.gov "Rule 10" "erroneous factual findings"`.
3. Search: `Parr v United States 351 U.S. 513 1956 final decision ends litigation merits nothing left execute judgment`.
4. Open attempted: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

## CourtListener MCP

1. `search(type="o", citation="349 U.S. 322", num_results=1)`: returned an unrelated 1997 Farmington River Power opinion. Disregarded; did not read its full text.
2. `search(type="o", q='caseName:"Lawlor"', court="scotus", filed_before="1956-01-01", num_results=3, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`: located Lawlor v. National Screen Service Corp., June 6, 1955, 349 U.S. 322, opinion 105314. Other results were historical orders in Lawlor, not the target case.
3. `search_document(opinion_id=105314, query="precludes", snippet_size=2200)`: read claim/issue-preclusion distinction and subsequent-conduct reasoning around pp. 326-328. Used in the forecast rationale.
4. `search(type="o", q='caseName:"Parr"', court="scotus", filed_after="1956-01-01", filed_before="1957-01-01", num_results=2, fields=["caseName","dateFiled","citation","opinions","absolute_url"])`: located Parr v. United States, June 11, 1956, 351 U.S. 513, opinion 105416.
5. `search_document(opinion_id=105416, query="ends", snippet_size=1000)`: read appellate-posture context around pp. 517-518.
6. `search_document(opinion_id=105416, query="terminates", snippet_size=1100)`: read the finality standard on p. 518. Used in the forecast rationale.

No case-specific external retrieval was undertaken. No target-petition outcome material was encountered. The linked injunction denial was present in the provisioned baseline and is a different event.
