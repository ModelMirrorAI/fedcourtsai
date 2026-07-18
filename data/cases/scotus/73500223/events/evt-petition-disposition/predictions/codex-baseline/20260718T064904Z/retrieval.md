# Retrieval

## Corpus and base rates

- Read `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” the originating-court, relist, CVSG, and Term tables; read the 2025 paid/IFP detail in `metrics/statpack.json`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
  - `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
  - The returned recent grants were broad SCOTUS comparators rather than subject-matched cases because SCOTUS topic metadata is sparse. Several had multiple distributions or a CVSG, reinforcing the value of those procedural signals but not supplying a close merits analogue.

## CourtListener MCP

- Opinion search: `type=o`, query `"PruneYard" "Cedar Point"`, filed June 23, 2021 through July 18, 2026, ordered by relevance (8 results). This surfaced *Cedar Point Nursery v. Hassid*, 594 U.S. 139, and a small set of later decisions rather than a developed lower-court split on the petition's precise question.
- Opinion search for *CDK Global LLC v. Brnovich*, 16 F.4th 1266 (9th Cir. 2021), to identify the opinion record.
- CourtListener opinions endpoint, opinion 5125303, for *CDK Global*. The relevant takings discussion treated *Cedar Point* as reaffirming *PruneYard* and relied on the distinction for property voluntarily opened to occupation by others.

No general web search was used, and no search sought this case's disposition or subsequent history.
