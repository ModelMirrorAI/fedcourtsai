# Retrieval log

- Read `metrics/statpack.md`, especially "Modern discretionary-cert petitions by disposition" and the adjacent circuit, relist, CVSG, and Term sections, for a general SCOTUS petition base-rate reference. The resolved modern discretionary-cert slice reports 10 grants, 189 denials, and 5 dismissals (4.9% grants), but it is not directly comparable to an original habeas petition.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '518 U.S. 651' --limit 5 --corpus-backend ranged` to retrieve corpus priors involving the principal original-habeas authority. The lookup failed because the runner could not resolve the corpus remote's host; it returned no priors and printed no `ranged corpus reads: ...` line.
- CourtListener MCP opinion search: `"Rule 20" "writ of habeas corpus" "exceptional circumstances"`, restricted to SCOTUS opinions filed before July 10, 2025, to identify the governing original-habeas standard. It returned *Felker v. Turpin* and *Hohn v. United States*.
- CourtListener MCP opinion search: `"adequate relief" "exceptional circumstances" "writ of habeas corpus"`, restricted to SCOTUS opinions filed before July 10, 2025, to confirm the standard and related authorities. It returned *Felker v. Turpin*, *In re McDonald*, and *Hohn v. United States*.
- CourtListener MCP citation search for `518 U.S. 651` to identify the *Felker* opinion record. The useful result was *Felker v. Turpin*, cluster/opinion 118058; two lexical false matches were ignored.
- CourtListener MCP opinion endpoint lookup for opinion 118058, requesting `id` and `html_with_citations`, to read *Felker*'s statement of Rule 20.4(a) and its treatment of original habeas relief.

No REST fallback or web search was used, and no retrieval concerned this case's disposition or subsequent history.
