# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-23.json`, `context.json`,
`documents/petition.txt`, `documents/questions-presented.txt`, `documents.json`) and the
committed `metrics/statpack.md`:

## Corpus (`fedcourts query`, read-only via the cell's corpus service)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s`
   stderr: `ranged corpus reads: 49 GET(s), 12713984 byte(s)`
   Returned recent granted rows led by substantive emergency applications (26A308, 26A388);
   not a cert comparator set.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-09-22`
   stderr: `note: replay cutoff 2026-09-22 (from --decided-before) — priors that had not resolved by then are excluded, on top of any --decided-before Term`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned 20 granted rows (four stay applications, sixteen plenary cert grants from
   OT2024–OT2025 with distribution counts 1–22). Used only for shape; no Indian-law prior
   surfaced.

## CourtListener MCP

3. `search` type=o, court=ca8, q=`"Andeavor Logistics" trespass allottees` → 2 results:
   *JoAnn Chase v. Andeavor Logistics, L.P.*, 12 F.4th 864 (8th Cir. 2021, No. 20-1747,
   Published) and *JoAnn Chase v. Andeavor Logistics, L.P.* (8th Cir. Jan. 30, 2026,
   No. 23-3019, Published, cluster 10781861). Opinion text not read.
4. `search` type=d, court=scotus, docket_number=`26-388` → 0 results (this docket is not in
   CourtListener's RECAP index; no post-snapshot entries were seen).
5. `search` type=d, court=scotus, q=`"Bad River Band" Enbridge` → 0 results (no companion
   petition on the Seventh Circuit pipeline-trespass case surfaced).

No web searches. Nothing retrieved disclosed this petition's disposition.
