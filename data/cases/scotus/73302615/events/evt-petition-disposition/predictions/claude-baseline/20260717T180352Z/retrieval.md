# Retrieval log — scotus/73302615, evt-petition-disposition, claude-baseline, 20260717T180352Z

## Corpus CLI

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   — returned 8 granted 2020s SCOTUS priors (generic context; none FSIA-specific).
   stderr: `ranged corpus reads: 148 GET(s), 38666240 byte(s)`
2. `uv run fedcourts query --court scotus --citation '581 U.S. 170' --limit 3`
   — **failed**: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`. No transfer line.
3. `uv run fedcourts query --court scotus --citation '604 U.S. 115' --limit 3`
   — **failed**: same sidecar timeout. No transfer line. Not retried (sparse-filter etiquette).

## Base rates

- Read committed `metrics/statpack.md` (modern discretionary-cert base rates,
  originating-circuit cut, relist/CVSG cuts, per-Term table) and
  `metrics/statpack.json` (per-fee-class grant rates: paid ≈ 5.4% T2025 / 6.9% T2024).
  Note: the "Segment base rate by salience band" table referenced by the predict
  prompt is not present in the committed statpack.

## CourtListener MCP

1. `search(type=o, q="Helmerich Payne Petroleos de Venezuela", court=cadc, filed_after=2025-09-01)`
   — confirmed the decision below: *Helmerich & Payne Int'l Drilling Co. v.
   Petroleos de Venezuela, S.A.*, No. 24-7161 (D.C. Cir. Oct. 3, 2025), published
   (opinion id 10690213). No judge/panel metadata in the result.
2. `call_endpoint(opinions, id=10690213)` — returned the opinion row (no
   author/joined-by strings populated).
3. `call_endpoint(clusters, id=10223623)` — returned a mismatched cluster
   ("Wilkins v. United States", 2023-12-08); the id filter did not behave as a
   lookup. Abandoned rather than retried; the panel/dissent question was resolved
   from the petition itself (no dissent claimed anywhere in it).

## Web searches

None.

No retrieval touched this case's own disposition (none exists — forward cell,
petition pending; BIO due 2026-08-07).
