# Retrieval Log

## Corpus CLI Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Returned 10 recent resolved SCOTUS 2020s `denied` rows (`scotus/9526000623`, `scotus/9526000634`, `scotus/9526000637`, `scotus/9526000644`, `scotus/9526000636`, `scotus/9526000602`, `scotus/9526000612`, `scotus/9526000619`, `scotus/9526000606`, `scotus/9526000613`).

2. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 10`
   - Transfer: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Returned 10 recent resolved SCOTUS 2020s `gvr` rows (`scotus/73317900`, `scotus/73500268`, `scotus/73500579`, `scotus/9026000139`, `scotus/9026005216`, `scotus/73280412`, `scotus/73280426`, `scotus/73393227`, `scotus/73500363`, `scotus/9026000048`).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Clark v. Sweeney"`, `num_results=5`, `fields=["caseName", "dateFiled", "citation", "cluster_id"]`)
   - Returned 1 match (`Clark v. Sweeney`, `cluster_id: 10741339`, `dateFiled: 2025-11-24`), confirming the recent SCOTUS summary reversal cited in the petition.

2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Margolin v. National Association of Immigration Judges"`, `num_results=5`, `fields=["caseName", "dateFiled", "citation", "cluster_id"]`)
   - Returned 0 matches in the CourtListener opinion index.

3. `mcp_courtlistener_search` (`type="r"`, `case_name="Hamrit v. Citigroup Global Markets"`, `num_results=5`, `fields=["caseName", "dateFiled", "docketNumber", "court_id"]`)
   - Returned 1 match (`Hamrit v. Citigroup Global Markets, Inc.`, `court_id: "nysd"`, `docketNumber: "1:22-cv-10443"`, `dateFiled: "2022-12-09"`), matching the originating district court docket described in `petition.txt` and `appendix.txt`.

## Web Searches
- None.
