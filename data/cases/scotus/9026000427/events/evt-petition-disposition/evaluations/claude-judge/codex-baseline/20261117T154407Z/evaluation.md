# Evaluation — codex-baseline

**Cell.** `scotus/9026000427`, `evt-petition-disposition`, stage `cert`, forward. Outcome: petition **denied** on 2026-11-16 after a single distribution, no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.005 → `correct` = 1, Brier = 0.005² = 0.000025. Base rate, basis and skill are the harness's to stamp; I wrote none.

## Reasoning (`reasoning_quality` 0.9)

The strongest rationale of the three on method. It states its information set, pools the frozen band's reached rate over strictly prior Terms and says the numerator is approximate, and explicitly treats the relist/CVSG/amicus cuts as overlapping terminal-state populations that give shape rather than multipliers. That caveat is correct and the other candidates do not make it.

The case analysis is careful and accurate against the provisioned petition: QP 2 is identified as the only question with reach beyond this employee, the absence of competing appellate holdings is noted, and it correctly records that the administrative judge's alternative protected-disclosure finding was not reached by the full Board. It verified *Bosley* at the source and caught that *Bosley* (1998) predates *Morgan* (2002), declining to adopt the petition's framing. It also refuses to treat empty web responses as authority.

I graded its base-rate figures against the build it was placed against (`statpack-at`, build `7bcde3b105cb`, landed 2026-10-28), not today's refreshed pack; the zero-relist row (n=10,203, about 1.8% grant family) and the sal-v4 baseline reached figures match.

Short of the top: like the others, the step from about 5.1% to 0.5% is a judgment with no measured pro se or waiver rate behind it, and some space goes to tooling narration rather than analysis.

## Predicted reasoning (`predicted_reasoning_quality` 0.82)

Central claims: denial in an orders list after the November 13 conference, in mid-to-late November, with zero further distributions; no CVSG and the waiver standing without further briefing; an unexplained denial with no separate writing. All borne out: the petition was denied on November 16 after its one distribution, with no noted dissent. The timing commitment is the most specific of the three and it held. It stays below 1.0 because the calls were the strongly favoured ones on this record. The QP 2 narrowing and the 85/15 plenary split are conditional on a grant and are neither credited nor penalised.

## Leakage

Forward; `not_applicable`. Captured calls show the provisioned record, statpack, generic corpus queries (the single legible document date, 2026-04-29, predates resolution and belongs to unrelated cases), and a CourtListener read of *Bosley*. Three web calls are `unobserved`; graded on their queries, they concern Rule 10 and the Court's rules PDF, not this case. One search excluded `data/qp-topics` by glob, which is not a read.

## Big case

My read: 0.04. An individual pro se federal employee's pay and position-description dispute, dismissed on jurisdictional pleading grounds in a nonprecedential decision, with no amicus interest and a denial without comment.
