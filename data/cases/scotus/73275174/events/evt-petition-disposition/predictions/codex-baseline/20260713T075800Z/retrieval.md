# Retrieval log

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” and “SCOTUS cert petitions by Term,” for aggregate grant-rate context. No `fedcourts query` or `fedcourts open-events` invocation was made.
- CourtListener MCP opinion search: `type=o`, query `"Section 2" "private right of action" "Voting Rights Act"`, filed before 2025-08-26, eight results. Purpose: identify pre-filing appellate treatment of private Section 2 enforcement without querying this case.
- CourtListener MCP opinion search: `type=o`, query `"Voting Rights Act" "private right of action"`, court `scotus`, filed before 2025-08-26, ten results. Purpose: identify pre-filing Supreme Court authorities relevant to the implied-right question.
- CourtListener MCP opinion endpoint lookup for item `9442991`. Purpose: retrieve the Eighth Circuit opinion; the identifier was a cluster ID rather than an opinion ID, so the endpoint returned an unrelated historical opinion. It was not used.
- CourtListener MCP opinion search: `type=o`, query `"AR State Conference NAACP" "private right of action"`, court `ca8`, filed before 2025-08-26. Purpose: resolve the cluster to the underlying opinion ID.
- CourtListener MCP opinion endpoint lookup for item `9900816`, fields `id`, `cluster`, and `html_with_citations`. Purpose: verify the Eighth Circuit's holding and the competing statutory arguments in 86 F.4th 1204.

No REST fallback or web search was used, and no search targeted this case or its disposition.
