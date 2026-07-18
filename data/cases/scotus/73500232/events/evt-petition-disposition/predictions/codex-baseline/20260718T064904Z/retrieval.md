# Retrieval

## Corpus and committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, Term, and fee-class rates.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --limit 10`
  - `ranged corpus reads: 432 GET(s), 113246208 byte(s)`
  - The returned recent resolved SCOTUS rows supplied only broad context and were not treated as factually similar precedents.

## CourtListener MCP

- Opinion search: `"Rule 4(a)(5)" "excusable neglect" Pioneer circuit split`, limited to SCOTUS and the Third Circuit (no results).
- Opinion search: `"Rule 4(a)(5)" "excusable neglect" Pioneer` (127 results; reviewed the leading result metadata).
- Opinion search: `"Rule 58" "separate document" "150 days" notice of appeal` (165 results; reviewed the leading result metadata).
- Citation analysis of the petition's principal authorities, including *Pioneer*, *Stutson*, *Ragguette*, *Cendant*, *Orthopedic Bone Screw*, *Indrelunas*, *Brown*, and *Koon*; all eleven citation strings were verified or matched to the identified clusters, with two reporter strings returning duplicate/ambiguous clusters.
- Opinion search for `"Ragguette v. Premier Wines"` in the Third Circuit, then fetched opinion 806695, *Ragguette v. Premier Wines & Spirits*, 691 F.3d 315 (3d Cir. 2012), including its discussion of Rule 4(a)(5), *Pioneer*, and the reason-for-delay factor.
- Three searches for the pre-certiorari lower-court record in *Bank of New York Mellon v. Mazza*, No. 24-2794 (opinion full-text query, case-name query, and RECAP query); no results were returned.
- Opinion search: `"Rule 58(a)(5)" "Rule 60" separate document`, then fetched opinion 622452, *United States v. Lawuary*, 669 F.3d 864 (7th Cir. 2012).

No web searches were used, and no search sought this petition's disposition.
