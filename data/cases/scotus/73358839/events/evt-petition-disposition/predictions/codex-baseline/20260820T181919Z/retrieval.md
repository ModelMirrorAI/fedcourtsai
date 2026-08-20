Beyond the provisioned event, snapshot, and context, I consulted `metrics/statpack.md` and `metrics/statpack.json` for the sal-v3 baseline-band risk-set anchor, Fifth Circuit disposition cut, relist cut, and CVSG cut. No `fedcourts query` or `fedcourts open-events` corpus lookup was used, so there is no ranged corpus-read line.

CourtListener MCP lookups:

- RECAP search for Fifth Circuit docket 24-40792, identifying *Texas Top Cop Shop v. Blanche* and CourtListener docket 69450356.
- Docket-entry schema lookup and docket-entry query for docket 69450356, used to confirm that the Fifth Circuit appeal remained active; the returned material included the August 10, 2026 caption letter and lower-court briefing.
- Opinion search for `"Texas Top Cop Shop"`, which returned references in *Trump v. CASA, Inc.*
- Opinion search for `McHenry v. Texas Top Cop Shop`, which returned no results.
- Broad opinion search for `Texas Top Cop Shop Corporate Transparency Act`; results were noisy and did not materially affect the forecast.
- Dockets endpoint lookup for SCOTUS No. 25-1201, identifying *National Small Business United, dba National Small Business Association v. Scott Bessent* and CourtListener docket 73281689.
- Docket-entry lookup for CourtListener docket 73281689, which returned no entries.
- Opinion search for *National Small Business United*, identifying the Eleventh Circuit's December 16, 2025 decision in No. 24-10736.
- Cluster lookup for cluster 10760279 and metadata lookups for opinion records 11225788 and 11226864.
- Document read for opinion 11225788, which returned no available text.
- Document read for opinion 11226864, chunk 0, used for the Eleventh Circuit's holdings that the CTA regulates economic activity substantially affecting interstate commerce and does not facially violate the Fourth Amendment.

No web search was used.
