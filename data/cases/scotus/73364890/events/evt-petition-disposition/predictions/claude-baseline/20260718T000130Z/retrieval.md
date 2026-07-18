# Retrieval log — scotus/73364890 / evt-petition-disposition / claude-baseline / 20260718T000130Z

## Corpus lookups (`fedcourts`)

- `uv run fedcourts query --court scotus --citation "470 U.S. 564" --limit 3` —
  **failed**: `corpus service at http://127.0.0.1:8377 is unreachable — is the
  sidecar running? (fedcourts corpus-serve): timed out`. No
  `ranged corpus reads:` line was printed (the service never answered). No
  further `fedcourts query` calls attempted; fell back to the committed
  statpack per the degraded-upstream rule.

## Base rates

- Read the committed `metrics/statpack.md`: "Modern discretionary-cert
  petitions by disposition", relist-count cut (0 relists → 0.8% granted),
  CVSG cut (none → 3.0% granted), originating-circuit cut (ca11 → 4.4%
  granted), and the per-Term table (Terms 2023–2025 grant rates 2.5–3.3%).
  The statpack version in this checkout carries no "Segment base rate by
  salience band" table, so anchoring used the relist/CVSG/circuit cuts.

## CourtListener MCP

- `search(type=o, court=ca11, q="F.E.B. Corp" Wisteria Island)` — confirmed
  the prior published history: *United States v. F.E.B. Corp.*, 52 F.4th 916
  (11th Cir. 2022) (FEB II) and *F.E.B. Corp. v. United States*, 818 F.3d 681
  (11th Cir. 2016) (FEB I); the Nov. 2025 FEB III decision is unreported and
  not in the opinion index. No information about this petition's disposition
  was sought or surfaced.

## Web searches

- None.
