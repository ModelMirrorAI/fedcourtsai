# Retrieval log — scotus/73357827, run 20260718T000130Z

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`.
   Used to observe the docket-signal profile of recently granted petitions
   (all carried multiple conference distributions, unlike this case's single
   future long-conference distribution).

## Committed base-rate artifacts

- `metrics/statpack.md` — modern discretionary-cert base rates, originating-
  circuit (ca7), relist, and CVSG cuts, per-Term table. (No salience-band
  section exists in the committed statpack version, so no band anchor was
  available.)
- `metrics/statpack.json` — per-Term, per-fee-class detail (Term 2025 paid
  grant rate ≈ 5.4%; IFP ≈ 1.1%).

## CourtListener MCP lookups

1. `search(type=d, court=scotus, party_name="Wisconsin Voter Alliance")` — 0 results.
2. `search(type=d, court=scotus, q="Wisconsin Voter Alliance" OR "Wisconsin Voters Alliance")` — 0 results.
3. `search(type=d, court=scotus, q='"Help America Vote Act" cert petition 21112')` — 0 results.

SCOTUS docket coverage in the RECAP search index was too thin to surface the
petitioner's prior filings or comparable HAVA petitions; no case-specific facts
were taken from these searches, and nothing outcome-revealing about this
pending case was encountered. Knowledge of WVA's prior 2020-election
litigation comes from citations inside the petition itself.

No web searches were performed.
