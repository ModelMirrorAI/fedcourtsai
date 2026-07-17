# Retrieval log — scotus/73281628, evt-petition-disposition, claude-baseline, 20260717T000329Z

Mode: `forward` (pending case; unrestricted retrieval). Nothing about this
case's own disposition was sought or surfaced — the petition is undecided
(BIO due 2026-07-22).

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "340 U.S. 36" --corpus-backend ranged --limit 8`
   — priors citing Munsingwear. **0 rows.**
   stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --citation "599 U.S. 465" --corpus-backend ranged --limit 8`
   — priors citing Jones v. Hendrix. **0 rows.**
   stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
3. `uv run fedcourts query --court scotus --disposition gvr --corpus-backend ranged --limit 8`
   — recent GVR-disposition priors. **8 rows** (incl. Wells v. Texas 25-484,
   Newberry v. Texas 25-862, Grayson v. United States 25-851, United States
   v. Johnson 25-551 (CA4), Walters v. Coleman 25-867 (CA4), American Gas
   Ass'n v. DOE 25-879, Whitton v. Dixon 25-580) — used to confirm summary
   GVRs are a routine, current-Term disposition channel and that CA4 cases
   appear in it; Whitton also shares Arnold & Porter counsel (Andrew Tutt)
   with this petition.
   stderr: `ranged corpus reads: 19 GET(s), 4980736 byte(s)`

## Base rates

- Committed `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition" (grants a few percent of resolved), originating-circuit cut
  (ca4: denied 93.5% / granted 4.6% / dismissed 2.0%), relist and CVSG cuts,
  and the per-Term table (Term 2025 est. grant rate 2.5%). The salience-band
  table referenced in the prompt is not present in the committed statpack, so
  I anchored on the circuit/relist/CVSG cuts instead.

## CourtListener MCP lookups

1. `search` (opinions, published, filed after 2023-06-01, all circuits):
   `"Jones v. Hendrix" "saving clause" constitutional "Suspension Clause"` —
   0 results.
2. `search` (opinions, published, filed after 2023-07-01, all courts):
   `"Jones v. Hendrix" "Suspension Clause" § 2241` — 1 result: the decision
   below itself, Jason Bell v. J. Streeval (CA4, 2025-08-06), confirming it
   is the published decision under review; no wave of parallel published
   post-Jones Suspension Clause rulings surfaced under this phrasing.

## Web searches

None.
