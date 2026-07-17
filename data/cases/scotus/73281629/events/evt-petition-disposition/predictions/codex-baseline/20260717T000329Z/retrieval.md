# Retrieval beyond the provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md` and the paid-fee-class detail in `metrics/statpack.json`. Relevant anchors were the modern discretionary-cert, originating-circuit, relist, CVSG, and 2025 Term paid-petition cuts.

## Corpus lookup

- Attempted: `uv run fedcourts query --court scotus --era 2020s --citation '29 U.S.C. § 1024(b)(4)' --limit 8`
  - The lookup failed before returning rows because DNS resolution for the ranged corpus endpoint failed (`EndpointConnectionError`). No `ranged corpus reads: …` line was printed because no ranged read completed.

## CourtListener MCP

- Opinion search: `type=o`, query `"claims administration agreement" "1024(b)(4)"`, filed before `2026-07-17`, 10 results requested. It returned four results, led by *Mondry v. American Family Mutual Insurance*, 557 F.3d 781 (7th Cir. 2009).
- Opinion search: `type=o`, query `"administrative services agreement" "1024(b)(4)"`, filed before `2026-07-17`, 10 results requested. It returned 13 matches, led by *M. S. v. Premera Blue Cross*, 118 F.4th 1248 (10th Cir. 2024), and also surfaced *Hively v. BBA Aviation Benefit Plan* and *Mondry*.
- Targeted opinion search for *M. S. v. Premera Blue Cross*, Tenth Circuit, filed October 1, 2024. It returned the published decision and CourtListener opinion id 10594949.
- Opinion endpoint lookup for id 10594949, limited to `id` and `html_with_citations`. The opinion confirms that the Tenth Circuit affirmed the § 1024(b)(4) violation as to the administrative services agreement while distinguishing other non-governing criteria.

No general web search was used, and no lookup sought this case's disposition.
