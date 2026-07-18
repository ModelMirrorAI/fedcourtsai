# Retrieval consulted

## Committed base rates

- `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- `metrics/statpack.json`, 2025 Term fee-class detail (paid estimated grant rate 5.36%; IFP estimated grant rate 1.12%).

## CourtListener MCP

All three opinion searches were limited to material filed before the May 28, 2026 petition date, so they could not surface this petition's disposition. Each returned `HTTP 429` with the message that the 1,200-per-day rate limit was exceeded and an expected availability in approximately 230 seconds; no result content informed the forecast.

- Opinion search: `q=\"18 U.S.C. § 242\" \"bodily injury\" \"de minimis\"`, `filed_before=2026-05-28`, 8 results requested.
- Opinion search: `q=\"18 U.S.C. § 242\" willfulness Screws \"specific intent\"`, `filed_before=2026-05-28`, 8 results requested.
- Opinion search: `q=\"Barnes v. Felix\" \"totality of the circumstances\" excessive force`, `filed_after=2025-05-14`, `filed_before=2026-05-28`, 8 results requested.

No corpus query or web search was used.
