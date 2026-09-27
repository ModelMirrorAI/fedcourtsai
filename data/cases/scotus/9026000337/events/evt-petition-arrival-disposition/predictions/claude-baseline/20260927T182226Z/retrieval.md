# Retrieval log

Beyond the provisioned inputs (`record/context.json`, `record/snapshots/2026-09-15.json`, `record/documents/documents.json`, `petition.txt`, `questions-presented.txt`, the event definition, `metrics/statpack.md`):

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 49 GET(s), 12713984 byte(s)`
  Returned 20 rows, mostly OT2026 substantive interim applications (26A308, 26A388, 26A326, 26A274, 26A203, 26A124) and two OT2025 plenary grants (25-246, 25-238). No comparable diversity/insurance petition; recorded for provenance only.

## CourtListener MCP (`courtlistener` server, `search` tool)

1. `type=o, court=ca8, filed_after=2026-01-01, q="Child v. Unum Life Insurance guaranteed issue existing loss"` — 1 result: Denise Child v. Unum Life Insurance Co. of America, 8th Cir. No. 24-2347, filed 2026-05-11, status Published (cluster 10856965). Confirms the decision below is published.
2. `type=d, court=scotus, docket_number=26-337` — 0 results. No docket or disposition surfaced for this petition.
3. `type=o, q="guaranteed issue" "long-term care" "existing loss" OR "postclaims underwriting" OR "post-claims underwriting"` — 11 results; the only on-point hit is the Eighth Circuit opinion itself, the rest are Affordable Care Act cases matching "guaranteed issue". No other appellate decision on the question.
4. `type=o, court=[iowa, iowactapp, ca8, iand, iasd], q="514G" "preexisting condition" long-term care` — 0 results. No indexed Iowa authority construing the provision.

## Web

None.
