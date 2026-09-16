# Retrieval log

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73281372 --event evt-petition-disposition --role predictor` — path resolution only.
- `uv run fedcourts query --court scotus --citation "583 U.S. 366" --limit 3` — attempt to pull Merit Management as a prior. Returned **no rows**; stderr:
  - `ranged corpus reads: 1357 GET(s), 355532800 byte(s)`
  - `note: citations filter: 200 of 590880 rows in scope (scotus) carry citation data, and the column holds a case's OWN reporter cites (not a cases-citing-this-authority graph) — an empty result here usually means missing data, not no match`
- `metrics/statpack.md` (committed): modern discretionary-cert disposition table; originating-circuit cut (ca2 row); relist-count and CVSG-status cuts (paid scored segment); per-Term table; *Segment base rate by salience band (sal-v4)* — pooled the `baseline` bracketed `reached` figures for OT2017–OT2024.

## CourtListener MCP (forward mode — unrestricted; 6 calls)

1. `search type=d court=scotus docket_number=25-1089` — 0 results (SCOTUS dockets are not indexed in RECAP docket search).
2. `search type=d court=scotus q="Picard safe harbor 546(e)"` — 0 results (looking for prior Madoff safe-harbor petitions as priors).
3. `search type=d court=scotus case_name="Deutsche Bank Trust Company Americas v. Robert R. McCormick Foundation"` — 0 results (looking for the Tribune petition's CVSG history).
4. `call_endpoint dockets id=73281372` — confirmed: scotus, No. 25-1089, filed 2026-03-17, `date_terminated: null`, last modified 2026-06-18. Used only to confirm the petition is still pending; no outcome material.
5. `search type=o citation="147 F.4th 136"` — 0 results.
6. `search type=o court=ca2 case_name="Fairfield Sentry" filed_after=2025-01-01` — 1 result: *In re Fairfield Sentry Ltd.*, filed 2025-08-05, Nos. 22-2101-bk(L), 23-965(L), published; no judge metadata returned. Did not read the opinion body.

## Web searches

None.

## Not consulted

Nothing under `data/qp-topics/`; no other predictor's output; no outcome file.
