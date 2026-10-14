# Retrieval record

## Local material beyond the provisioned record

- Read the task contract and output schemas; resolved the event path with `uv run fedcourts paths --court scotus --docket 9026000274 --event evt-petition-disposition --role predictor`.
- Read the relevant cert sections of `metrics/statpack.md` and corresponding Term/segment fields in `metrics/statpack.json`. Computed the sal-v4 baseline reached pool over 2017–2025: 643 / 12,877. No current-Term rate entered the anchor.
- No `fedcourts query` or `open-events` calls; consequently no ranged-corpus transfer lines were produced. No local or remote corpus blob was read.

## Web attempts

The following `web.run` requests returned no visible usable source text or search results in this session and supplied no factual support:

- Search: `site.supremecourt.gov "Lopez" "21-7624" "opposition"`.
- Search: `"United States v. Mannava" "Hart" "elements"`.
- Search: `site.supremecourt.gov "Barrett" "2026" "482"`.
- Search: `"Barrett v. United States" "24-5774" "pdf"`. The docket string was a search hypothesis, not a verified identifier or a source relied upon.
- Attempted opening of the Cornell U.S. Code section 18 U.S.C. 2422 page.

## CourtListener MCP

1. Opinion search by citation `565 F.3d 412`, two-result limit: returned United States v. Mannava, decided May 15, 2009, opinion 1210801.
2. `read_document(opinion_id=1210801)`: read returned opinion text, with displayed-output truncation.
3. `search_document(opinion_id=1210801, query="elements", snippet_size=850)`: read the predicate-elements/unanimity discussion directly.
4. Opinion search by citation `635 F.3d 850`, one-result limit and selected fields: returned United States v. Hart, decided March 29, 2011, opinion 213491.
5. `search_document(opinion_id=213491, query="Mannava", snippet_size=1800)`: read the express disagreement over specific-predicate unanimity.

These lookups concern older, different cases. No lookup sought this cell's disposition, subsequent history, current docket, or an outcome-bearing artifact. No outcome-revealing material for this petition surfaced.
