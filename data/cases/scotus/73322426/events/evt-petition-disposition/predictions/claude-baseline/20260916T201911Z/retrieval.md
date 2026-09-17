# Retrieval log — claude-baseline, scotus/73322426, run 20260916T201911Z

Forward-mode cell; retrieval unrestricted. Nothing about this case's own
disposition was sought or seen (the petition is pending).

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
  Returned four recent granted application dockets (26A-series, distribution
  count 0) and four relisted OT2025 cert grants (25-246, 25-238, 25-566,
  25-965; distribution counts 3, 22, 17, 5). Used only as a contrast profile
  for what granted petitions' distribution histories look like.

## Statpack

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition",
  "Cert petitions by relist count (paid scored segment)", "Cert petitions by
  CVSG status (paid scored segment)", "Cert petitions by salience band", and
  "Segment base rate by salience band (sal-v4)" (pooled `baseline` bracketed
  `reached` over OT2017–OT2024 ≈ 5.1%).

## CourtListener MCP

1. `search` (type `o`, court `mont`, q `"two-way video" "Confrontation Clause" Johnson`,
   filed after 2026-01-01) → 1 result: State v. Johnson, 2026 MT 32, DA 23-0581,
   filed 2026-02-24, cluster 10799916.
2. `search` (type `d`, court `scotus`, q `"two-way video" "Confrontation Clause"`,
   filed after 2019-01-01) → 0 results (SCOTUS docket text is not indexed for
   this query).
3. `call_endpoint` `opinions` (cluster 10799916, fields id/type/author_str/
   per_curiam/joined_by_str) → one combined opinion, author McKinnon, no
   separate writing listed.

## Web fetches (supremecourt.gov, URLs taken from the snapshot's docket entries)

- Brief in Opposition of the State of Montana (filed 2026-09-04), PDF, 86 pages
  with supplemental appendix; text extracted locally with pypdf.
- Reply Brief for Petitioner (submitted 2026-09-15), PDF, 13 pages; text
  extracted locally with pypdf.

Both were on the provisioned docket but absent from `record/documents/`
(fetched 2026-07-17, before they were filed).
