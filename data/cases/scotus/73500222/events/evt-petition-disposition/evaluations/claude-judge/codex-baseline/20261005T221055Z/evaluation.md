# Evaluation of codex-baseline — Karsjens v. Gandhi, No. 25-1321 (scotus/73500222), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on
2026-10-05 after a single distribution (conference of 9/28/2026), with no noted
dissent from denial. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.045 − 0)² = 0.002025.
- `segment_base_rate` = 0.0512, basis `risk_set`. Frozen `band: baseline` with
  `salience_version: sal-v4`, matching the statpack table's heading, so the
  bracketed `reached` figures apply, pooled resolved-weighted over the rendered
  Terms strictly before OT2025 (OT2017–OT2024; the caption renders 10 of 10
  Terms, so no window divergence): 592.9 / 11,580 ≈ 5.12%. The candidate's own
  pooling arrives at the same figure.
- `brier_skill_score` = 1 − 0.002025 / 0.0512² ≈ **+0.23**: modestly better than
  the naive base-rate forecast on a denial.
- `judgment_correct` null, no `vote_accuracy`: non-merits cell. No
  `semantic_grades`: cert cell, and `semantic_claims` is null.

## Reasoning quality: 0.85

A careful, well-sourced rationale. The anchor is derived exactly as the contract
asks (reached rates, strictly-prior rendered Terms, weighted by n, rounding
caveat stated), and the candidate explicitly declines to use the terminal rates
or the pack-wide figures as substitutes. The case analysis goes to the primary
materials: it reads the Eighth Circuit opinion in the appendix and identifies the
real ground of decision (the unaddressed 2013 joint recommendation to split
Rule 706 expert fees and the plaintiffs' failure to explain why it should not be
relied on), notes that the lower court itself allows indigency to justify
withholding costs, and so sees that the case is a poorer vehicle than the
petition's framing suggests. It independently verified Stanley's costs discussion
through CourtListener rather than taking the petition's word, and correctly
confines the second question to record-specific error correction with an
Excessive Fines argument never reached below. The waiver is weighed as modest
negative evidence with the CFR path kept open, which is the right posture at a
single pre-conference distribution. The net adjustment (down from 5.1% to 4.5%)
is consistent in direction with the factors listed, and the limits (no BIO,
unverified oral-argument account, failed web calls) are disclosed.

Deductions: the downward move is small relative to the weight of its own
negatives (waiver, record-specific ground, no amicus, long-conference slot), so
the number is somewhat under-committed; the candidate stops short of saying what
a grant would structurally require (a CFR before any grant), which is the
strongest reason a waived, once-distributed petition is below the reached-band
rate; and the orientation figures from the pack-wide and circuit cuts, while
flagged as orientation only, add length without moving the analysis.

## Leakage

`mode` = forward; `influenced_prediction` = `not_applicable`,
`retrieved_outcome_material` = false, `leakage_suspected` = false.
Mis-provisioning check: created 2026-09-17, before the 9/28 conference and the
10/05 denial. Of 28 logged calls (`result_capture_coverage` 0.89), the captured
ones are prompt, schema, record and statpack reads plus two CourtListener lookups
of Stanley v. USC (1999), a historical authority; the three web-search rows are
unobserved and graded on their queries, which name Rule 54 generically and a 2014
Ninth Circuit PDF, never this petition. No `retrieved_doc_date` is set anywhere.
The rationale states it neither sought nor encountered this petition's outcome
and that its procedural read is limited to the provisioned snapshot. Nothing
indicates a decided case provisioned forward.

## Big case (independent read): 0.15

A Rule 54(d)(1) costs-discretion question with a thin, old disagreement framed
as a discretionary factor, a record-specific second question, no amicus, a
waiver, one distribution, and a bare denial. Sympathetic facts but low-visibility
stakes outside civil-procedure specialists. The predictor's `big_case_score` was
visible in the staged `prediction.json` when it was read, so this read is
independent in basis but not strictly in sequence.
