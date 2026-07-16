# Retrieval beyond the provisioned inputs

## Corpus and base rates

- Read `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit, relist-count, CVSG, and per-Term sections.
- Read the 2025 Term paid/IFP detail in `metrics/statpack.json`. The paid-petition estimated grant rate was 5.36%.
- Attempted: `uv run fedcourts query --court scotus --citation 'Carlson v. Green' --era 2020s --limit 10` (with the runner package cache redirected to `/tmp`). The ranged corpus endpoint failed DNS resolution before any result or read statistics were produced. No `ranged corpus reads: …` line was emitted.

## CourtListener MCP

- Searched opinions filed from 2024-01-01 through 2026-07-16 in the First, Third, Fourth, Fifth, Seventh, Ninth, Tenth, and Eleventh Circuits for `"Carlson v. Green" Bivens medical`. The responsive results included *Laquan Johnson v. Elaine Terry*, 119 F.4th 840 (11th Cir. 2024).
- Searched Supreme Court opinions filed from 2022-01-01 through 2026-07-16 for `Bivens Carlson`. Results included *Goldey v. Fields*, 606 U.S. 942 (2025), and *Egbert v. Boule*, 596 U.S. 482 (2022).
- Searched specifically for *Goldey v. Fields* and retrieved the full text of CourtListener opinion item 11086520. The opinion granted certiorari and summarily reversed an Eighth Amendment excessive-force Bivens extension while identifying prison administration, congressional action, and alternative remedies as special factors.
- Inspected the CourtListener `dockets` endpoint schema, then queried SCOTUS docket 25-417. It identified *Francis Nielsen v. Kekai Watanabe*, docket ID 73278422, with no termination date.
- Inspected the `docket-entries` endpoint schema, then queried entries for docket ID 73278422. CourtListener returned no entries, so this lookup supplied no conference or disposition information.

No web searches were used.
