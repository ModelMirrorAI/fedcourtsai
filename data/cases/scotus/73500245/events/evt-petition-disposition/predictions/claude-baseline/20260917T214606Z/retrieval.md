# Retrieval log — scotus/73500245 / evt-petition-disposition / claude-baseline / 20260917T214606Z

Mode: `forward` (`record/context.json`); no `DECIDED_BEFORE` clock in the environment. One corpus query and five CourtListener MCP calls, well under the advisory budget. Nothing about this petition's own disposition was sought or seen; it cannot exist before the September 28, 2026 conference.

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Purpose: recent resolved SCOTUS denials for context. Returned five September 2026 denials (Lee v. Lovelace, Vermont Information Processing v. NLRB, Norman v. Texas, USPS v. California, Conahan v. Florida). Context only; did not shape the number.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (pooled `baseline` bracketed `reached` rate over OT2017–OT2024 ≈ 5.1%).
- `metrics/statpack.json`: originating-court bucket "Supreme Court of Alabama" (29 resolved, 28 denied, 1 granted).

## CourtListener MCP lookups

1. `search` type=d, court=scotus, docket_number=25-1344 — 0 results (CourtListener does not carry this SCOTUS docket).
2. `search` type=o, court=ala, q=`Blevins "Alabama State Bar"`, filed_after=2025-01-01 — found *Jerry M. Blevins v. Alabama State Bar*, SC-2024-0693, filed 2025-12-19, published (cluster 10761703).
3. `search` type=d, court=almd, q=`Blevins Stewart "Alabama State Bar"`, filed_after=2026-01-01 — found *Blevins v. Stewart*, 2:26-cv-00133, § 1983 civil-rights suit filed 2026-03-01, not terminated (the pending federal action the petition lists as related).
4. `call_endpoint` opinions, cluster=10761703 — read the Alabama Supreme Court per curiam opinion below (affirmed; Sellers and Parker, JJ., concurring; Stewart, C.J., and Shaw, Bryan, Mendheim, and McCool, JJ., concurring in the result; Wise and Cook, JJ., recused).

## Web searches

None.
