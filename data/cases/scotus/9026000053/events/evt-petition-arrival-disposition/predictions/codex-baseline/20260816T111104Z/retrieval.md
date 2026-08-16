# Retrieval

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. The strictly prior OT2017-OT2025 sal-v3 baseline risk set pooled to 863/13,163 = 6.56%. The paid grant-family split contained 300 explicit GVR labels among 863 rows (34.8%); I treated that as an incomplete route proxy, not the true cert-order share.
- CourtListener MCP search: `type=d`, `court=scotus`, `docket_number=25-1383` (query `61ca396b`). No result.
- CourtListener MCP search: `type=o`, `court=ca5`, `case_name="Town of Vinton v. Indian Harbor Insurance"`, filed before 2026-08-17 (query `f2e9f713`). No result.
- CourtListener MCP search: `type=o`, `court=ca5`, `q="\"Town of Vinton\" \"Indian Harbor\""`, filed before 2026-08-17 (query `df76ce8c`). It returned the published December 8, 2025 *Town of Vinton v. Indian Harbor* opinion and a separate *Police Jury* opinion.
- A parallel read-only evidence check searched for and read the *Town of Vinton* Fifth Circuit opinion (CourtListener opinion 11215982). One intermediate lookup mistakenly treated cluster 10749397 as an opinion id and returned an unrelated document; that document was disregarded.

No `fedcourts query` or `fedcourts open-events` corpus lookup was used.
