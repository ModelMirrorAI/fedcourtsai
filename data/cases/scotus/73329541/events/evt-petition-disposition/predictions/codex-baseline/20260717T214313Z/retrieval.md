# Retrieval

No `fedcourts query` or `open-events` corpus lookup was used. No web search was used.

## Base rates

- Read `metrics/statpack.md`, especially the modern discretionary-cert, originating-circuit, relist-count, CVSG, and per-Term tables.
- Read the 2025 Term paid-filing detail in `metrics/statpack.json`.

## CourtListener MCP

All lookups were confined to legal context or lower-court material predating the predicted disposition; none sought this petition's disposition.

1. Opinion search for `Bowe v. United States`, Supreme Court, January 1–July 17, 2026. Found *Bowe v. United States*, No. 24-5438, decided January 9, 2026, cluster 10772450.
2. Opinion search for `"2244(d)(1)" AND "2241"` through July 17, 2026. Reviewed the returned circuit authorities and metadata, including *Dulworth v. Evans* and later cases.
3. Expanded opinion search for `Bowe v. United States` requesting docket, opinion, and syllabus metadata. Identified combined opinion 11239035.
4. Opinion endpoint lookup for opinion 11239035, requesting `html_with_citations`. Consulted the *Bowe* syllabus and majority's statutory analysis.
5. Opinion search for `Cox v. McBride`, Seventh Circuit, 2001–2003. Found 279 F.3d 492 and combined opinion 776425.
6. Opinion search for `Dulworth v. Evans`, Tenth Circuit, 2005–2007. Found 442 F.3d 1265 and combined opinion 167281.
7. Opinion search for `Galbraith v. Hooper`, Fifth Circuit, 2025–July 17, 2026. Consulted result metadata only; no proposition from the opinion affected the forecast.
8. Opinion endpoint lookup for opinion 776425, requesting `html_with_citations`. Consulted *Cox*'s distinction between state-court custody and additional custody imposed by a disciplinary board.
9. Opinion endpoint lookup for opinion 167281, requesting `html_with_citations`. Consulted *Dulworth*'s holding that § 2244(d)(1) applies to § 2241 administrative challenges by people in state-court custody.
10. Opinion search for `St. Clair v. Quick`, Tenth Circuit docket 24-7090, filed October 16–18, 2025. No result.
11. Opinion search for `"Michael St. Clair" AND "Christe Quick"`, Tenth Circuit, January 1, 2025–February 7, 2026. No result.
12. Opinion search for `Bowe AND "2241" AND "2244(d)"`, January 9–July 17, 2026. No result.
