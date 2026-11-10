# Evaluation — claude-baseline, scotus/9026000462 (Hauber v. Honkamp Krueger & Co.), evt-petition-disposition

**Stage:** cert (forward, `moment: distribution`). **Outcome:** denied 2026-11-09, no noted dissent, no CVSG, two distributions.

## Scores
- Predicted `denied` at P(grant) = 0.006 → `correct` = 1, `brier_score` = 0.000036.
- `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are left for the harness stamp (cert cell, frozen `baseline` band under `sal-v4`); I quote no rate of my own. Votes are not scored on a cert cell.

## Reasoning quality — 0.85
The rationale anchors on the correct figure for a frozen band: the baseline band's bracketed risk-set (`reached`) rate pooled over strictly-prior Terms. It then makes concrete, well-sourced downward adjustments: pro se paid petitioner, an abuse-of-discretion review of a Rule 37(b)(2) sanction dismissal, a respondent waiver with no likely call for a response, and no intervening decision that could support a GVR. It uses the lower-court docket to reconstruct the posture because the petition text could not be extracted, and it says plainly that its read of the question is inferred from that posture. The question presented (due process limits on a sanction dismissal while a disability-accommodation motion was pending) fits that inference, and the forecast document even names the accommodation grievance. The best analytical point is that the frozen distribution count of 1 belonged to the sealing motion, not to the petition. Docket text proves that right. The deduction is for the size of the jump from about 5% down to 0.6%. That is defensible, but it rests on judgement rather than a measured pro se rate, which the candidate admits.

## Predicted reasoning — 0.75
Central claims, in order: (1) a denial without separate writing, which held; (2) exactly one more distribution, for the petition itself, and no relist after it, which held: the petition was distributed Oct 14 for the Nov 6 conference and denied Nov 9; (3) the timing window (distribution Oct 21–28 for Nov 7/14, denial Nov 10/17), which missed by about a week; (4) no CVSG, which held; (5) the conditional summary route, which stays unresolved. The document is specific, and its distribution call was one a reader could have got wrong by trusting the frozen count. One secondary claim, the timing, failed, which puts it at the 0.75 anchor.

## Leakage
Forward. The prediction was made 2026-10-08, before the 2026-11-09 denial. The log has full result capture. The latest retrieved document date is 2026-08-10, an N.D. Iowa entry. There is no query for the SCOTUS disposition and no `qp-topics` read. Graded `not_applicable`, so `leakage_suspected` = false.

## Semantic grades
Cert cell: no semantic set is declared, so none was written.
