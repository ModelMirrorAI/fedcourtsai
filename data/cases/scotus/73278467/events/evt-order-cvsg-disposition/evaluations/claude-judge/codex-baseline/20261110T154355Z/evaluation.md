# codex-baseline — evaluation

## Outcome

Cert-stage cell (moment `cvsg`). After the June 30, 2026 CVSG, the Solicitor General filed on September 25, 2026, recommending that the Court grant, vacate, and remand in light of *West Virginia v. B.P.J.* and *United States v. Skrmetti*. The petition was distributed on October 14 for the November 6 conference, and on November 9, 2026 the Court entered a GVR "in light of *West Virginia* v. *B. P. J.* … and *United States* v. *Skrmetti*." So `actual_disposition` is `gvr` and `actual_granted` is 1.

Every candidate scores `correct` = 0: no candidate predicted `gvr`, and `granted` and `gvr` are distinct labels. `brier_score` is `(p − 1)²`. The anchor (`segment_base_rate`, `brier_skill_score`, `base_rate_basis`) is left to the harness. Each prediction froze `band: high` under `sal-v4`, so the anchor is the stamped segment base rate over that risk set. I quote no rate of my own.

**Leakage.** Every candidate ran forward on 2026-09-18. That was before the SG brief (9/25) and before the GVR (11/9), so no outcome material existed to retrieve. `influenced_prediction` is `not_applicable` and `leakage_suspected` is false. The details are in `leakage.notes`.

**Semantic grades.** None: this is a cert cell with no declared semantic set.

**Big case (my read, 0.5).** The question is important and recurring: *Turner* deference versus heightened scrutiny for sex-based jail policies. Twenty-three states filed as amici and the federal BOP has an interest. But the Court disposed of the petition by GVR and decided nothing itself, and the vehicle is a pleading-stage case with a preservation problem.

## Scores

- Prediction: `denied`, p = 0.43. `correct` = 0 and `brier_score` = 0.3249. Wrong direction on the label and on the binary side of 0.5.

## Reasoning quality — 0.55

`reasoning.md` is disciplined:
- It uses a strictly prior-Term high-band anchor (about 35.0%) and keeps the CVSG cut as context rather than double-counting it.
- It cites the petition and the brief in opposition by page.
- It states its uncertainty about the SG's recommendation candidly.

It also identified the mechanism that actually decided the case. In its words, "the alternative GVR route materially sustains the grant probability," resting on the petition's reliance on the *Fowler* vacatur in light of *Skrmetti*. It checked *Skrmetti*'s scope and concluded that this "favors reconsideration." Its decomposition gave about 24% to a cert-order disposition, 19% to a plenary grant, and 55% to denial.

The weakness is calibration of the headline number. It gave the vehicle objections, which bear on plenary review, enough weight to keep denial modal. It did not see that those same objections make a GVR more attractive, not less, which is what the SG argued. It also did not weigh *B.P.J.* (decided the day of the CVSG) as a second GVR trigger. The analysis is good, but it netted out on the wrong side.

## Predicted reasoning — 0.30

Central claims, in order:
1. **Denial is the most likely outcome.** This is the headline call, it is specific, and it failed.
2. **Conditional on any grant, a cert-order GVR is the principal route (0.55), driven by the *Fowler*/*Skrmetti* history.** Borne out, and specifically so.
3. **At least one further distribution after the SG's brief.** Borne out.
4. **Disposition in October Term 2026, after the SG's input.** Borne out.

The writing-on-denial claim was conditional on a denial that did not occur. A failed headline call with a discriminating secondary route call that held sits just above the 0.25 anchor.
