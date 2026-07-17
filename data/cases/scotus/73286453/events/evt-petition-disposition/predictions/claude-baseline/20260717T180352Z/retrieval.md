# Retrieval log — scotus/73286453 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Beyond the provisioned inputs (snapshot, questions-presented, petition, brief
in opposition), I consulted:

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert base rates, originating
  circuit (ca11), relist-count, CVSG, and per-Term tables.
- `metrics/statpack.json` — per-Term fee-class detail (paid-class grant rates:
  ~5.4% Term 2025, ~6.9% Term 2024).

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   - stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
   - Purpose: profile what recent granted petitions look like. Takeaway: the
     retrieved grants carried multiple conference distributions (3–22) and
     Supreme Court specialist counsel (Clement, Frederick, Sauer, Thompson,
     Unikowsky) — both absent here.

## CourtListener MCP lookups

1. `search(type=d, court=scotus, case_name=McKinney, q="Dean McKinney")` — 0
   results. Checked whether the losing defendant in Dean v. McKinney (4th Cir.
   2020) sought cert; no SCOTUS docket found.
2. `search(type=d, court=scotus, q="\"South Bend\" Flores")` — 0 results. Same
   check for Flores v. City of South Bend (7th Cir. 2021); no SCOTUS docket
   found.
   - Takeaway from both: the Browder/Dean-vs-Hughes conflict does not appear
     to have been presented to the Court before — a fresh vehicle, mildly
     grant-positive. Neither search surfaced anything about this case's own
     disposition.

## Web searches

None.
