# Retrieval and tooling record

## Local context and corpus

- Read the event definition, case-level context, and provisioned snapshot `2016-11-04.json`; the record listing contained no filed documents or related snapshots.
- Read `metrics/statpack.md`, specifically the interim application section and prior-Term coverage. No eligible 2006–2015 resolved substantive observations support a baseline for Term 2016. Later and current-Term rows were not used as forecast inputs.
- Attempted `uv run fedcourts paths --court scotus --docket 72406996 --event evt-motion-disposition --role predictor`. It failed because the default uv cache location was read-only. Retried with `UV_CACHE_DIR=/tmp/uv-cache`; the retry resolved the expected case and event paths without reading an outcome.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` and subsequently displayed its beginning again to confirm the structured filters.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2010s --disposition denied --decided-before 2016 --limit 5`. It exited successfully but returned no prior rows. Stderr: `ranged corpus reads: 917 GET(s), 240123904 byte(s)`. This was a broad historical-prior lookup, not a search for Arthur or his disposition. No empirical analogues were available from this result and no further corpus scan was attempted.

## Web attempts

- Attempted one `web.run` search call containing `site.supreme.justia.com Barefoot Estelle 463 880 stay execution reasonable probability four justices` and `site.supreme.justia.com Hill McDonough 547 573 stay execution equitable remedy 2006`.
- Attempted to open the Barefoot opinion page on Supreme Justia and then find `reasonable probability` on that page.
- Those web calls provided no usable returned text in this session. No web material was used as factual support; CourtListener supplied the relevant precedent instead. No search was directed to Arthur, 16A450, or 16-595.

## CourtListener MCP

- `search(type="o", citation="463 U.S. 880", num_results=1)` returned a broad citation match headed by Aranda v. Dal-Tile Corp., January 11, 2016, rather than the requested Barefoot opinion. The unrelated result was not used as a prior.
- `search(type="o", court="scotus", case_name="Barefoot v. Estelle", filed_before="2016-01-01", num_results=3)` returned Barefoot, 463 U.S. 880 (July 6, 1983), and two 1983 procedural orders. Only the principal opinion was used.
- `search_document(opinion_id=111017, query="reasonable probability", snippet_size=1100)` returned the passage requiring a prospect of review, possible reversal, and irreparable harm for an execution stay. Used as general pre-boundary legal context, not as evidence about Arthur's grounds.

## Prior knowledge

Possible historical-outcome memory is disclosed in `reasoning.md` and `flags.json`. No case-specific later history was intentionally retrieved, and no evaluator-only or other predictor material was read.
