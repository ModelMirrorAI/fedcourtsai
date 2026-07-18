# Retrieval

## Committed base-rate context

- `metrics/statpack.md`, sections “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- `metrics/statpack.json`, 2025 Term paid-fee-class details.
- `uv run fedcourts query --help` was consulted to inspect the corpus-query interface. It performed no corpus lookup and printed no `ranged corpus reads` line. No `fedcourts query` or `open-events` corpus retrieval was used.

## CourtListener MCP

1. Opinion search for `"21 U.S.C. § 360bbb-3" "private right of action"`, limited to filings before 2026-07-18 (query `777a7a59`); five results, including *Pearson v. Shriners Hospitals*, 133 F.4th 433 (5th Cir. 2025), and *Curtis v. Inslee* (9th Cir. 2025).
2. Cluster lookup for CourtListener cluster 10371624 initially requested an unavailable `opinions` field and returned a field-validation error; no substantive data was used from that failed request.
3. Cluster lookup for 10371624 using valid fields identified the published *Pearson* opinion and sub-opinion 10838212.
4. Opinion lookup for 10838212 retrieved the published *Pearson* text. The response was truncated, but included the relevant holding that § 360bbb-3 does not restrict a private employer's vaccination policy and the court's express reservation of the implied-right question.
5. Opinion search for `"option to accept or refuse" "private right of action" vaccine`, limited to filings before 2026-07-18 (query `e3ab3919`); four results, including *Pearson* and *Curtis*.
6. Cluster lookup for CourtListener cluster 10691522 identified the published *Curtis v. Inslee* opinion and sub-opinion 11158110.
7. Opinion lookup for 11158110 retrieved the published *Curtis* text. The response was truncated, but included its holding that § 360bbb-3 does not create a private right enforceable under § 1983.

No open-web search was used, and no lookup sought this petition's disposition.
