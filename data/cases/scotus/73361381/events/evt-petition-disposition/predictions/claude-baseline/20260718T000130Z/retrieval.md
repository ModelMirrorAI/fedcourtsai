# Retrieval log — scotus/73361381 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Mode: `forward` (pending petition; retrieval unrestricted, outcome does not exist).

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   — stderr: `ranged corpus reads: 431 GET(s), 112852992 byte(s)`
   — pulled recent resolved SCOTUS priors for context (mostly high-salience
   granted/denied cases from the June 30, 2026 conference; no close comparable
   to a pro se state-court insurance petition, so base rates carried the weight).

## Base rates

- `metrics/statpack.md` (committed) — modern discretionary-cert disposition
  split, relist/CVSG cuts, originating-court table (state intermediate courts),
  per-Term table.
- `metrics/statpack.json` — per-Term fee-class detail (Term 2025 paid
  est. grant rate 5.4%, IFP 1.1%). Note: the "Segment base rate by salience
  band" table referenced in the prompt is not present in the committed statpack.

## CourtListener MCP lookups

1. `search(type=d, court=scotus, q="Chaganti")` — 0 results (no prior SCOTUS
   dockets for this party in the RECAP docket index).
2. `search(type=r, party_name="Chaganti")` — 30 results across federal courts
   (district, bankruptcy, criminal), confirming the petitioner's frequent-
   litigant profile. No query touched this case's own disposition (none exists;
   the petition is pending, distributed for the 2026-09-28 conference).

## Web searches

None.
