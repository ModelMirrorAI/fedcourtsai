# Retrieval beyond the provisioned inputs

## Committed base-rate context

- Read the interim-applications section of metrics/statpack.md and its corresponding metrics/statpack.json rows. A local jq calculation pooled application Terms 2016–2025: 160 substantive grants / 1,366 substantive resolutions = 0.1171303075, with 16 unparsed applications. No live corpus retrieval was attempted; there is no ranged-corpus-reads line.

## Web calls

1. One web search call contained two queries: `site.supremecourt.gov "Dalton v. Specter" "statutory"` and `site.govinfo.gov "102(c)" "waive all legal requirements" "Constitution"`. The search returned a broad mixture of material, including extraneous results; I did not rely on those results as case-specific evidence or open any result about this application's disposition.
2. Opened the official GovInfo HTML public-law text at `https://www.govinfo.gov/content/pkg/PLAW-109publ13/html/PLAW-109publ13.htm`. This returned the REAL ID Act's public-law text and supplied general statutory context for the waiver and judicial-review provisions.
3. Ran a find call on that same GovInfo page for `waive all`, locating the general waiver provision. No search of this application's current status or outcome was attempted.

## CourtListener MCP calls

1. `search(type="o", citation="511 U.S. 462", num_results=1)`: returned Dalton v. Specter, decided May 23, 1994, with opinion ID 1087960 and citation 511 U.S. 462. The response reported five matches and returned the requested leading case; I did not paginate.
2. `search_document(opinion_id=1087960, query="constitutional", snippet_size=650)`: returned 20 of 24 matching excerpts. These confirmed the distinction between a claim of exceeding statutory authority and a constitutional claim. This was authority retrieval, not retrieval of the application being forecast.

## Local operational checks

The first `uv run fedcourts paths --court scotus --docket 9526000560 --event evt-brief-response-disposition --role predictor` failed because the default uv cache location was read-only. Retrying with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. The path listing did not disclose an outcome path, and no outcome was opened. Repository schema, identifier, path, and serialization helpers were inspected to construct and validate the output; those were operational inputs, not additional case evidence.
