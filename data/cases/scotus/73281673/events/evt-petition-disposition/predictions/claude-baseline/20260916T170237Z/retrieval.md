# Retrieval log

Provisioned inputs read: `event.yaml`, `record/snapshots/2026-09-15.json`,
`record/context.json`, `record/documents/{documents.json,
questions-presented.txt, petition.txt, brief-in-opposition.txt}`, plus
`metrics/statpack.md` (modern-cert, relist, CVSG, salience-band, and per-Term
sal-v4 band tables) and the three output schemas.

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73281673 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
  stderr: `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
  (structured filters only; returned recent granted rows, none on this topic —
  used to confirm the tool works, not as priors)

## CourtListener MCP

1. `search` type=d court=scotus q="CyberTip OR ... NCMEC" filed_after 2024-06-01 → 0 results
2. `search` type=o q="Gasper Snapchat 'private search'" → State v. Gasper, 2026 WI 3 (cluster 10774319)
3. `search` type=d court=scotus q="private search" (hash OR CyberTipline ...) → 0 results
4. `search` type=d court=scotus case_name=Maher OR Lowers OR Holmes OR Wilson OR Braun → 0 results
5. `search` type=o courts ca7/ca4/ca2/ca9 q="private search" CyberTip ... filed_after 2025-06-01 → 0 results
6. `search` type=r court=ca7 docket_number=25-2740 → United States v. Braun docket 73330341
7. `search` type=d courts ca4/scotus case_name=Lowers → 0 results
8. `search` type=d court=scotus case_name=Maher filed_after 2024-10-01 → 0 results
9. `search` type=o court=ca7 case_name=Braun filed_after 2025-09-01 → clusters 10954196, 10954197 (decided 2026-08-20)
10. `get_endpoint_item` clusters/10954197 → opinion 11421796 (Brennan, C.J., concurring)
11. `get_endpoint_item` clusters/10954196 → opinion 11421795 (Lee, J., majority)
12. `read_document` opinion 11421795 chunks 0–2 (majority: background, preservation, probable cause)
13. `read_document` opinion 11421796 chunk 0 (duplicate header text)
14. `read_document` opinion 11421796 chunks 5–6 (Brennan concurrence on private-search doctrine and split)

Nothing retrieved concerned this petition's own disposition; all material
predates the 2026-09-15 snapshot. No web searches.
