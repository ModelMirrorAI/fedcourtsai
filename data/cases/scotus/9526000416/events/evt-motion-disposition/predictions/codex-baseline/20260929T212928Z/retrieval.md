# Retrieval record

## Local materials beyond the provisioned case record

- Read AGENTS.md, .github/prompts/predict.md, prediction and feedback schemas for the contract.
- Read metrics/statpack.md, particularly the interim table, and inspected the top-level keys of metrics/statpack.json. No case membership or outcome rows were retrieved. Used the strictly prior application-Term pool: 31 substantive grants / 296 resolutions.
- Ran uv run fedcourts paths --court scotus --docket 9526000416 --event evt-motion-disposition --role predictor. The initial invocation failed because the default uv cache was read-only; the invocation with a writable temporary cache succeeded. No outcome file was opened.
- Inspected fedcourtsai.paths, fedcourtsai.ids, and fedcourtsai.serialize for path and artifact conventions. No corpus query or open-events command was run; no ranged corpus reads line was emitted.

## Web attempts

Three web.run search batches returned no usable results or source text. Exact queries:

1. site.supremecourt.gov opinions 2025 Skrmetti 24-110 pdf
2. site.supremecourt.gov Nken Holder stay likelihood irreparable injury 2009
3. site.supremecourt.gov "Skrmetti" "24-110" "2025"
4. site.supremecourt.gov "Nken" "556" "418"
5. site.supremecourt.gov/opinions/24pdf/ "Skrmetti" "23–477"
6. site.supremecourt.gov/opinions/24pdf/ "Wages" "White Lion"

The first Skrmetti searches used an incorrect docket number; no results from them informed the forecast. No search named this application's parties or sought its disposition.

## CourtListener MCP

1. search(type="o", case_name="Nken v. Holder", court="scotus", num_results=2, filed_before="2026-09-28"). Returned the April 22, 2009 decision, 556 U.S. 418, opinion 145884.
2. search_document(opinion_id=145884, query="four factors", snippet_size=1600). Read two excerpts, including the four stay factors and the relative importance of the first two at pages 434–435. Used as general legal context only.
3. search(type="o", case_name="United States v. Skrmetti", court="scotus", filed_before="2026-09-28", num_results=1). Returned metadata for the June 18, 2025 decision, 605 U.S. 495, docket 23-477, opinion 11243418. Did not paginate.
4. search_document(opinion_id=11243418, query="Held:", snippet_size=1400). Returned: "No text is available for this document." No holding inferred from the failed text lookup; the application's invocation of the case was treated as advocacy.

No outcome-revealing material about the target application was encountered. No direct CourtListener REST calls were made.
