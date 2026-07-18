# Retrieval log — scotus/73500250 · evt-petition-disposition · claude-baseline · 20260718T064904Z

## Committed base rates

- `metrics/statpack.md` — modern discretionary-cert base rates, originating-circuit,
  relist, CVSG, and per-Term tables (no salience-band section is present in the
  committed statpack version).
- `metrics/statpack.json` — per-Term per-fee-class detail (paid vs IFP grant rates,
  OT2023–OT2025).

## Corpus lookups (`fedcourts query`, service backend)

1. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
   → `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   (recent granted petitions; noted multiple-distribution/relist pattern before grants)
2. `uv run fedcourts query --court scotus --era 2020s --limit 8`
   → failed: `corpus service at http://127.0.0.1:8377 is unreachable ... timed out`
   (no transfer line; retried with the narrower query below)
3. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 4`
   → `ranged corpus reads: 185 GET(s), 48496640 byte(s)`
   (rows not further used)

## CourtListener MCP lookups (forward mode — unrestricted)

1. `search(type=d, court=scotus, q="18 U.S.C. § 242" willfulness Screws)` → 0 results
   (no companion/related SCOTUS docket presenting the same Screws question)
2. `search(type=o, court=scotus, q=Screws willfulness "section 242" specific intent, filed_after=2015-01-01)`
   → 0 results (no modern SCOTUS opinion revisiting the § 242 willfulness standard)

Neither search touched this case's own disposition (none exists; the petition is
pending, distributed for the 2026-09-28 conference).

## Web searches

None.
