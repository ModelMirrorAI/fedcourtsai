# Retrieval beyond the provisioned inputs

## Corpus base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted the 2025 Term fee-class detail in `metrics/statpack.json`. It reports an estimated 5.36% grant rate for paid petitions; the originating-circuit table reports a 5.0% grant rate for modern Tenth Circuit petitions.
- No `fedcourts query` or `fedcourts open-events` lookup was made, so there is no ranged-corpus-read line to report.

## CourtListener MCP

All searches were limited to legal material available before this prediction and did not seek this Supreme Court petition's disposition.

1. Opinion search for `Rio Grande Foundation v. Oliver` in the Tenth Circuit, filed before 2026-07-17 (5-result limit). This identified the 2025 panel decision, the 2023 standing decision, and the 2025 rehearing order.
2. Opinion search for `Americans for Prosperity Foundation v. Bonta` in the Supreme Court (5-result limit). This identified 594 U.S. 595 (2021).
3. Opinion search for `"major purpose" "issue advocacy" donor disclosure exacting scrutiny`, filed before 2026-07-17 (10-result limit). This surfaced related circuit decisions including *Human Life of Washington v. Brumsickle* and *The Gaspee Project v. Mederos*.
4. Focused Tenth Circuit opinion search for `Rio Grande Foundation v. Oliver`, filed from 2025-09-01 through 2025-09-14, requesting panel and opinion metadata.
5. Opinions-endpoint lookup for opinion ID 11135093, requesting the Tenth Circuit opinion text.
6. A second opinions-endpoint lookup for opinion ID 11135093 to extract short passages around the governing standards, informational interest, narrow tailoring, facial-challenge posture, and the exacting-scrutiny concession from the otherwise lengthy response.
7. Opinion search for `campaign finance donor disclosure issue advocacy electioneering communications "Americans for Prosperity Foundation" narrow tailoring`, filed from 2021-07-01 through 2026-07-16 (15-result limit). This surfaced post-*Bonta* decisions including *No on E v. Chiu* and *Smith v. Helzer*.

No general web search was used.
