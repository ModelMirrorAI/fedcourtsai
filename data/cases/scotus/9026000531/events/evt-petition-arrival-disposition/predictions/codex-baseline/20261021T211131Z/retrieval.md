# Retrieval log

## Committed base-rate context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist/CVSG cuts, and the `sal-v4` per-Term segment table.
- Read the corresponding `metrics/statpack.json` segment fields. A local `jq` calculation pooled baseline reached rates for all displayed prior Terms, 2017–2025: 644 / 12,883 = 0.04998835674920438. No 2026 segment row was included in the anchor.
- No `fedcourts query` or `open-events` call was made; there is no ranged-corpus transfer line to report. No live corpus state or similar-case sample was retrieved.

## General precedent only

1. CourtListener MCP `search(type="o", citation="537 U.S. 522", num_results=1)` identified Clay v. United States, decided March 4, 2003, opinion 122265.
2. CourtListener MCP `search_document(opinion_id=122265, query="Finality attaches", snippet_size=800)` verified the collateral-review finality discussion at 537 U.S. 527. Used as general precedent, not as a lookup of this petition.
3. CourtListener MCP `search(type="o", citation="529 U.S. 473", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])` identified Slack v. McDaniel, decided April 26, 2000.
4. CourtListener MCP `search_document(opinion_id=9433937, query="When the district court denies", snippet_size=750)` verified Slack's two-part procedural-dismissal COA standard, 529 U.S. 484.

## Web attempts

- A web search requested `site.supremecourt.gov Clay United States 537 522 finality attaches certiorari 2003` and `site.supremecourt.gov Slack McDaniel 529 473 484 procedural grounds certificate appealability`. The tool returned no visible results or source text.
- A web open attempted the official GovInfo PDF for United States Reports, volume 537, page 522 (`USREPORTS-537-522.pdf`). It likewise returned no visible document. Neither web attempt supplied evidence; the successful MCP precedent lookups supplied the verification instead.

No search or lookup sought No. 26-531, its current docket, its disposition, its subsequent history, or outcome coverage. The provisioned petition's appendices supplied the older direct-review history; no earlier cert denial was treated as the target event's result.
