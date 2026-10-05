# Retrieval record

## Provisioned inputs

Read the event definition, context, October 4, 2026 snapshot, document manifest, questions presented, and selected substantive sections of the petition and opposition. No other predictor's output, realized outcome, or subsequent case history was consulted.

## Committed base-rate context

Read the modern-cert disposition, originating-circuit, paid-segment relist/CVSG, and sal-v4 prior-Term band tables in `metrics/statpack.md`. Read the matching prior-Term baseline risk-set fields in `metrics/statpack.json` and computed 638 / 12,720. Used `git log -1 --format='%h %cI' -- metrics/statpack.md` solely to identify the committed artifact's vintage.

## Corpus tooling

- `uv --no-cache run --no-sync fedcourts corpus-info`: failed with the service-backend explanation that there is no client-side corpus connection. No corpus freshness timestamps or case rows were returned; no ranged-read transfer line was printed.
- No `fedcourts query` or `open-events` lookup was made.
- Operational path resolution used `uv --no-cache run --no-sync fedcourts paths --court scotus --docket 9026000183 --event evt-petition-disposition --role predictor`. An initial ordinary `uv run` failed because the default cache path was read-only; the no-cache invocation succeeded. This returned paths, not outcome content.

## Web attempts: general law only

1. Search: `site.supremecourt.gov Rule 10 considerations governing review certiorari misapplication properly stated rule law`. No usable result returned.
2. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`. No usable content returned.
3. Repeated that open once; again no usable content returned.
4. Find `Review on a writ` in `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`. No usable content returned.

None supplied evidence or surfaced information about this petition.

## CourtListener MCP: older general precedent only

1. `analyze_citations` on Wal-Mart Stores, Inc. v. Dukes, 564 U.S. 338 (2011); Halliburton Co. v. Erica P. John Fund, Inc., 573 U.S. 258 (2014); and Tyson Foods, Inc. v. Bouaphakeo, 577 U.S. 442 (2016). Wal-Mart and Tyson Foods were individually marked FOUND. Halliburton was individually marked NOT FOUND despite the response's aggregate verification summary; I relied on the item-level statuses, not the inconsistent summary.
2. `get_endpoint_item(endpoint_id="clusters", item_id=3187592, fields=["id", "case_name", "sub_opinions", "date_filed"])`: identified the March 22, 2016 Tyson Foods opinion, ID 3187537.
3. `search_document(opinion_id=3187537, query="individual", snippet_size=400)`: returned excerpts on common and individual questions, predominance, representative proof, and defenses.
4. `search_document(opinion_id=3187537, query="When one or more", snippet_size=750)`: no literal match.
5. `read_document(opinion_id=3187537, chunk_size=6000, chunk_index=4)`: read the majority's discussion allowing some separately tried issues where common questions predominate and its context-dependent treatment of representative evidence.

No lookup requested this petition's disposition, its later history, or Detwiler's current disposition. No outcome-revealing material was encountered.
