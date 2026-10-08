# Evaluation of gemini-baseline — scotus/73500287, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The
petition in *Endure Industries, Inc. v. Vizient Inc.*, No. 25-1385, was
distributed once (June 24, 2026, for the September 28 conference) after the
respondent waived its response; a single amicus brief followed on July 16. The
Court denied the petition on October 5, 2026, with no call for a response, no
relist, and no noted dissent. `outcome.json`: `actual_disposition: denied`,
`actual_granted: 0`, `distribution_count: 1`.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.012 − 0)² = 0.000144.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction's frozen
  context carries `band: baseline` and `salience_version: sal-v4`, and the
  statpack's "Segment base rate by salience band (sal-v4)" heading matches, so
  the bracketed `reached` baseline figures were pooled resolved-weighted over
  the rendered Terms strictly before Term 2025 (2017–2024, weighted
  n = 11,580). The table renders 10 of 10 Terms, so the rendered window is the
  pack's whole window and no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000144 / 0.0512² ≈ 0.945.
- `vote_accuracy` omitted: cert stage, never scored.
- `reasoning_quality` = 0.68.

## What the reasoning got right and wrong

The candidate identified the decisive mechanism: a paid petition on a waiver
is not granted without a call for a response, so the grant path runs through a
response request that had not issued twelve weeks after distribution. It put
that hazard near 5% and derived P(grant) strictly below it, landing at 1.2%.
That is the correct causal structure and it produced the best-calibrated
number of the three against a denial. It also correctly read the fact-bound,
summary-judgment posture, the absence of institutional amicus support, and the
non-repeat-player petitioner as negatives.

Where it falls short of the stronger analysis on this cell: the anchor is the
single prior Term's `reached` figure (OT2024, 5.7%) rather than the pooled
prior-Term rate the table supports, a methodological shortcut even though the
version and figure type are right; the lower-court opinion was not consulted,
so the forfeiture point in the Fifth Circuit's footnote that undercuts the
asserted split is absent; and "a grant requires a response" is stated as a
rule where it is a near-universal practice. The document is compact and sound
but thin on the legal merits of the asserted conflict.

## Leakage

Forward mode. The captured log (25 calls, every result unobserved, which is
this engine's standing capture shape, so each call is graded on its query)
shows only reads of the provisioned record, prompt, schema and statpack, and
two free-text `fedcourts query` attempts the candidate reports as unsupported.
No external retrieval, no query touching this case's disposition, no
`data/qp-topics/` path, and no document dated at or after October 5, 2026. The
case was genuinely open on September 18, so `influenced_prediction` is
`not_applicable`, `retrieved_outcome_material` false, `leakage_suspected`
false.

## Big case

Independent read 0.2: a private antitrust market-definition dispute from the
Fifth Circuit, decided at summary judgment, with a waiver, one solo
practitioner amicus, and a silent denial. The Brown Shoe submarket question
recurs, but this vehicle carried no institutional stakes.
