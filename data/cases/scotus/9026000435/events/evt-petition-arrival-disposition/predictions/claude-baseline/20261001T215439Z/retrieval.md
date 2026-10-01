# Retrieval log — scotus/9026000435, evt-petition-arrival-disposition, claude-baseline, run 20261001T215439Z

Mode: `forward` (retrieval unrestricted; no outcome for this petition exists). Budget used: 1 corpus query, 5 CourtListener MCP calls.

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
  Result: 12 rows, 9 of them emergency applications (26A dockets) and 3 OT2025 cert grants with 2, 3, and 22 distributions; no row comparable to a private-petitioner NLRB enforcement case. Not used in the number.
- `metrics/statpack.md` (committed): sal-v4 segment base rate by salience band (baseline `reached` rate pooled over OT2017–OT2025 = 5.0%, n = 12,720); relist-count, CVSG, and originating-circuit cuts read for shape.

## CourtListener MCP

1. `search` type=o, court=ca2, q=`"Siren Retail" "National Labor Relations Board" "Loper Bright"`, filed_after 2026-01-01 → 1 result: Siren Retail Corp. v. NLRB, No. 24-3168, filed 2026-09-02, status Published (cluster 10964726). Confirms the petition's intra-circuit development. Opinion body not read.
2. `search` type=d, court=scotus, q=`"National Labor Relations Board" "Loper Bright"`, filed_after 2024-07-01 → 0 results.
3. `search` type=o, court=ca8, q=`"Multimedia KSDK" supervisor producers` → 6 results including Multimedia KSDK, Inc. v. NLRB, 303 F.3d 896 (8th Cir. 2002) (cluster 3029656) and the 2001 panel decision, 271 F.3d 744. Confirms the cited authority; body not read.
4. `search` type=d, court=scotus, case_name=`"National Labor Relations Board"`, filed_after 2024-10-01 → 0 results (CourtListener's SCOTUS docket index does not carry these).
5. `search` type=d, court=scotus, case_name=`"Hospital Menonita"` → 0 results.

No web searches. Nothing retrieved concerned this petition's own disposition.
