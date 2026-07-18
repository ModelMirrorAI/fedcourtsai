# Retrieval log — scotus/73351824 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Mode: `forward` (`record/context.json`).

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   - stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
   - Used for: profile of recently granted petitions (distribution counts,
     originating courts, counsel).
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - stderr: `ranged corpus reads: 201 GET(s), 52559872 byte(s)`
   - Used for: contrast set; showed distribution_count ≈ 3 is common even for
     denials, so raw distribution count was not treated as a grant signal.

## Base rates

- Committed `metrics/statpack.md` (modern discretionary-cert anchor, relist /
  CVSG / originating-court cuts, per-Term table).
- `metrics/statpack.json` for the per-fee-class detail (Term 2025 paid ≈ 5.4%
  grant; Term 2024 paid ≈ 6.9%).

## CourtListener MCP

The server's daily request quota was already exhausted (HTTP 429,
"Rate limit exceeded: 1200/day") for nearly the whole session.

- `search(type=d, court=scotus, q="Indian Child Welfare Act" certiorari, filed_after=2023-07-01)` → 0 results.
- `search(type=o, court=scotus, q="Indian Child Welfare Act", filed_after=2023-07-01)` → 429 (throttled), retried → 429.
- `search(type=d, court=scotus, q="ICWA" OR "Indian Child Welfare", filed_after=2023-07-01)` → 429, 429, then one success: **0 results** (CourtListener's docket index has little SCOTUS coverage).
- Final `search(type=o, …)` attempts → 429, 429.

Net: no usable CourtListener signal this run. The intended check — how the
Court has disposed of post-*Brackeen* ICWA cert petitions — could not be
verified, and the reasoning weights that consideration qualitatively only.
Per the contract, the degraded upstream degrades the cell; the prediction
rests on the provisioned snapshot, the petition documents, the statpack, and
the two corpus queries above.

No web searches were surfaced by the engine this run.
