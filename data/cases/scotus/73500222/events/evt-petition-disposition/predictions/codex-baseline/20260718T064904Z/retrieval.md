# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and “SCOTUS cert petitions by Term.”
- Consulted the 2025 Term paid-petition detail in `metrics/statpack.json` (estimated grant rate 5.36%).

## CourtListener MCP

1. Opinion search, filed before May 26, 2026: `"chilling effect" AND "Rule 54(d)" AND costs AND "civil rights"` (10 results requested; 62 matches). This identified Ninth Circuit and other cost-award authorities. It also returned the Eighth Circuit opinion already reproduced in the provisioned petition; no disposition of the Supreme Court petition was sought or surfaced.
2. Circuit-opinion search, filed before May 26, 2026: `("chilling effect" OR indigent) AND "civil-rights plaintiffs" AND "Rule 54(d)" AND costs` (20 results requested; no matches under the combined circuit filter).
3. Opinion search, filed before May 26, 2026: `"chilling effect of imposing such high costs" OR "chilling effect" "future civil rights litigants"` (20 results requested; 21 matches). Results included *Stanley*, *Association of Mexican-American Educators*, *Draper*, and decisions discussing related cost factors.
4. Opinion endpoint lookup for *Moore v. CITGO Refining & Chemicals Co.*, 735 F.3d 309 (5th Cir. 2013). The opinion describes the circuit variation over indigence, relative resources, chilling effects, and Rule 54's presumption.
5. Supreme Court opinion search, filed before May 26, 2026: `"Rule 54(d)(1)"` (20 results requested; 2 matches), identifying *Marx v. General Revenue Corp.* and *Taniguchi v. Kan Pacific Saipan, Ltd.* as modern Rule 54 decisions.

No corpus query was run because the available SCOTUS corpus filters do not carry subject-matter metadata suitable for finding genuinely similar Rule 54 petitions.
