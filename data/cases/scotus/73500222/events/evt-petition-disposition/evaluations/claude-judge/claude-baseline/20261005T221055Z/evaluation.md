# Evaluation of claude-baseline — Karsjens v. Gandhi, No. 25-1321 (scotus/73500222), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on
2026-10-05 after a single distribution (conference of 9/28/2026), with no noted
dissent from denial. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.02 − 0)² = 0.0004.
- `segment_base_rate` = 0.0512, basis `risk_set`. Frozen `band: baseline` with
  `salience_version: sal-v4`, matching the statpack table's heading, so the
  bracketed `reached` figures apply, pooled resolved-weighted over the rendered
  Terms strictly before OT2025 (OT2017–OT2024; the caption renders 10 of 10
  Terms, so no window divergence): 592.9 / 11,580 ≈ 5.12%. The candidate's own
  pooling arrives at the same figure.
- `brier_skill_score` = 1 − 0.0004 / 0.0512² ≈ **+0.85**: well ahead of the naive
  base-rate forecast on a denial.
- `judgment_correct` null, no `vote_accuracy`: non-merits cell. No
  `semantic_grades`: cert cell, and `semantic_claims` is null.

## Reasoning quality: 0.85

A disciplined rationale whose structure matches how the Court actually disposes
of a waived, once-distributed paid petition. The anchor is derived correctly
(reached rates, strictly-prior rendered Terms, weighted n, with the terminal
relist-0 figure named only as the floor), and every adjustment is tied to
something in the record. The strongest point is structural: a grant on a waiver
requires a call for a response, then a response, then a relist, and the petition
had passed none of those filters, which is why it belongs below the reached-band
rate rather than at it. The split is correctly characterized as thin, old
(Stanley 1999, AMAE 2000, Weever 1991) and framed as an abuse-of-discretion factor
rather than a rule of law, and the Court's recent Rule 54(d)/§ 1920 cases are
rightly distinguished as being about what is taxable, not about discretion to
deny. The vehicle analysis reaches the Eighth Circuit's real ground (the
unaddressed 2013 proposal to split Rule 706 fees, the halving of the award, the
Excessive Fines point never adjudicated). The litigation-history and
petition-quality points are fair and are the kind of thing conference-memo
readers weigh. The candidate is candid about what it could not do (both
CourtListener calls throttled, corpus queries surfaced no comparable priors) and
says which way that uncertainty cuts. The forecast's shape (no further
distribution, no CFR, no CVSG, bare denial) is what happened.

Deductions: the move to 40% of the anchor rests on a characterization of the
split as thin and un-deepened that the candidate admits it could not verify
live, and 0.02 leaves little room for the CFR path it itself describes as
possible; the assertion that this costs dispute has "already been to this Court
on its merits without a grant" is taken from the petition's recitals rather than
checked. Neither error changes the direction of the analysis.

## Leakage

`mode` = forward; `influenced_prediction` = `not_applicable`,
`retrieved_outcome_material` = false, `leakage_suspected` = false.
Mis-provisioning check: created 2026-09-17, before the 9/28 conference and the
10/05 denial. The log's 23 calls are fully captured (`result_capture_coverage`
1.0, 2 throttled). Two corpus queries returned recency-ranked priors with
`retrieved_doc_date` 2026-09-16, before the prediction and well before
resolution. Two CourtListener searches, one for the chilling-effect split and one
for this litigation's prior SCOTUS dockets by caption, both returned HTTP 429 with
no result; a forward cell may run a caption query in any case, and at that date
the docket showed no disposition. The rationale reads the snapshot's three
entries and no disposition. Nothing indicates a decided case provisioned
forward.

## Big case (independent read): 0.15

A Rule 54(d)(1) costs-discretion question with a thin, old disagreement framed
as a discretionary factor, a record-specific second question, no amicus, a
waiver, one distribution, and a bare denial. Sympathetic facts but low-visibility
stakes outside civil-procedure specialists. The predictor's `big_case_score` was
visible in the staged `prediction.json` when it was read, so this read is
independent in basis but not strictly in sequence.
