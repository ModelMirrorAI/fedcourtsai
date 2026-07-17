# Retrieval

Beyond the provisioned inputs, I consulted the committed `metrics/statpack.md` and `metrics/statpack.json` for modern certiorari base rates, including the Term 2025 paid-petition grant estimate, relist-count rates, and CVSG rates.

CourtListener MCP lookups:

1. Opinion search: `court=scotus`, query `"reserved powers doctrine" Winstar damages state contract` (5-result limit). This returned *United States v. Winstar Corp.*, 518 U.S. 839 (1996).
2. Opinion search: `court=scotus`, query `"bill of attainder" deceased punishment` (5-result limit). The returned results did not identify a modern Supreme Court merits decision applying the doctrine to a posthumous target.
3. Opinion search: query `"Hastings College Conservation Committee" California`, filed before April 27, 2026 (5-result limit). This located the pre-petition California appellate opinions, including the October 15, 2025 decision under review.
4. Opinion search by case name for *Hastings College Conservation Committee v. State of California*, filed October 15, 2025 (3-result limit), to identify the lower-court opinion record.
5. CourtListener opinion endpoint item `11171195`, fields `id` and `html_with_citations`, to examine the lower court's pre-petition reasoning and cited authorities.

No `fedcourts query` or `fedcourts open-events` lookup was used. No web search was used.
