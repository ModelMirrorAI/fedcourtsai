# Retrieval log — scotus/73500223 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Forward-mode cell; retrieval unrestricted. Nothing surfaced revealed this
petition's disposition (it remains pending, distributed for the 2026-09-28
conference).

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   — recent granted-cert priors, to read the distribution-count/relist
   pattern preceding grants.
   stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert base rates, relist and
  CVSG cuts, per-Term table.
- `metrics/statpack.json` — per-fee-class detail (paid vs IFP grant rates
  for Terms 2024–2025).

## CourtListener MCP lookups

1. `search(type=d, court=scotus, q="PruneYard overrule", order_by=dateFiled desc)`
   — 0 results (docket search does not surface petition text; no docket-level
   signal of parallel overrule campaigns).
2. `search(type=o, court=scotus, q="PruneYard", filed_after=2020-01-01)`
   — 6 results: *Moody v. NetChoice* (2024, incl. revision duplicates),
   *Cedar Point Nursery v. Hassid* (2021), *AID v. Alliance for Open
   Society* (2020). Confirms no post-2020 separate opinion (e.g., dissent
   from denial) urging *PruneYard*'s reconsideration; the recent mentions
   distinguish it.

## Web searches

None.
