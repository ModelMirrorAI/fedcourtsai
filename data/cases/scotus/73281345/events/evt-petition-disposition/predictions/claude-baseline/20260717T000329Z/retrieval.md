# Retrieval log — scotus/73281345 / evt-petition-disposition / claude-baseline / 20260717T000329Z

Forward-mode cell; retrieval unrestricted. Beyond the provisioned snapshot and
documents I consulted:

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (~3.1% grant), originating-circuit cut (ca5 4.8%), relist and CVSG cuts,
  per-Term table.
- `metrics/statpack.json` — per-fee-class detail: paid grant rate 5.4% (Term
  2025), 6.9% (Term 2024). Note: no "Segment base rate by salience band"
  section exists in the committed statpack (the prompt describes one); no
  salience-band anchor was available.

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "United States v. Lopez" --citation "Gonzales v. Raich" --limit 8`
   — 0 rows returned.
   `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --citation "514 U.S. 549" --limit 8`
   — 0 rows returned.
   `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

Neither citation-overlap query surfaced priors, so the quantitative anchor is
the statpack alone.

## CourtListener MCP lookups

1. `search(type=d, court=scotus, case_name="Chavarria", filed_after=2025-06-01)`
   — 0 results.
2. `search(type=d, court=scotus, q="Chavarria")` — 0 results.
3. `search(type=d, court=scotus, q='Bryan "United States" cyberstalking OR kidnapping OR instrumentality', filed_after=2025-08-01)`
   — 0 results.

Purpose: check for a pending government petition in *United States v.
Chavarria* (10th Cir. 2025) or a petition in *United States v. Bryan* (11th
Cir. 2025) that could serve as a companion/hold vehicle. None found. None of
these searches touched this case's own disposition.

## Web searches

None.
