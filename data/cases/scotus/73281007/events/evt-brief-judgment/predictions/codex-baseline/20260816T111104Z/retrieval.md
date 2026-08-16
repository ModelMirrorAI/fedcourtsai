# Retrieval

Beyond the provisioned case inputs, I consulted `metrics/statpack.md`, specifically “The merits docket (granted cases),” to calculate the strictly prior ten-Term window. The published OT2017–OT2024 rows contribute 359 disturbed / 515 parsed = 69.7%, with 515 / 557 (92.5%) parsed coverage and 57 reported pool-guard exclusions.

CourtListener MCP lookups:

- Opinion search for citation `146 S. Ct. 1418`, limited to material filed before July 28, 2026. It returned only unrelated legacy citation matches.
- Opinion search for citation `146 S. Ct. 1403`, limited to material filed before July 28, 2026. It returned no result.
- Opinion search by case name `FCC v. AT&T`, limited to January 1–July 27, 2026. It found the June 4, 2026 Supreme Court opinion cluster 10870061.
- Opinion search by case name `Sripetch v. SEC`, limited to January 1–July 27, 2026. It found the June 4, 2026 Supreme Court opinion cluster 10870059.
- Document search for `Justice` using cluster id 10870061 as an opinion id. It returned a 404 and supplied no evidence.
- Cluster endpoint lookup for `FCC v. AT&T` cluster 10870061, which identified opinion 11337518.
- Three searches within opinion 11337518 for `delivered the opinion`, `dissent`, and `We hold`. These established the 8–1 lineup and the Court's treatment of the FCC assessment as nonbinding before a de novo enforcement trial.
- Cluster endpoint lookup for `Sripetch v. SEC` cluster 10870059, which identified opinion 11337516.
- Three searches within opinion 11337516 for `delivered the opinion`, `We hold`, and `dissent`. These established the unanimous lineup and the opinion's treatment of disgorgement; the result was secondary context rather than a driver of the forecast.

No `fedcourts query` or `open-events` corpus lookup and no web search was used.
