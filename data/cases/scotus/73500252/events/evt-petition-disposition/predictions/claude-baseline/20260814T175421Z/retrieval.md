# Retrieval log — claude-baseline / 20260814T175421Z

Beyond the provisioned inputs (snapshot `2026-08-14.json`, `event.yaml`,
`record/context.json`, and the three provisioned document texts) and the
committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --citation "602 U.S. 205" --limit 3`
   — empty result (known coverage gap: only 161 of 590,020 scotus rows carry
   citation data).
   Transfer line: `ranged corpus reads: 1327 GET(s), 347865088 byte(s)`.

## CourtListener MCP lookups

All three were attempts to date the *Conti v. Citizens Bank* cert denial
relative to *Cantero III* (May 5, 2026); none succeeded — CourtListener's
index does not carry the SCOTUS *Conti* docket:

1. `search` (type `d`, court `scotus`, case_name "Conti v. Citizens Bank") — 0 results.
2. `search` (type `d`, court `scotus`, q "Citizens Bank") — 0 results.
3. `call_endpoint` (`dockets`, court `scotus`, case-name filter) — rejected;
   the endpoint accepts no case-name filter.

## Web searches

None.
