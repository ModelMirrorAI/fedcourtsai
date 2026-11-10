# gemini-baseline — evaluation

## Outcome

Cert-stage cell (moment `cvsg`). After the June 30, 2026 CVSG, the Solicitor General filed on September 25, 2026, recommending that the Court grant, vacate, and remand in light of *West Virginia v. B.P.J.* and *United States v. Skrmetti*. The petition was distributed on October 14 for the November 6 conference, and on November 9, 2026 the Court entered a GVR "in light of *West Virginia* v. *B. P. J.* … and *United States* v. *Skrmetti*." So `actual_disposition` is `gvr` and `actual_granted` is 1.

Every candidate scores `correct` = 0: no candidate predicted `gvr`, and `granted` and `gvr` are distinct labels. `brier_score` is `(p − 1)²`. The anchor (`segment_base_rate`, `brier_skill_score`, `base_rate_basis`) is left to the harness. Each prediction froze `band: high` under `sal-v4`, so the anchor is the stamped segment base rate over that risk set. I quote no rate of my own.

**Leakage.** Every candidate ran forward on 2026-09-18. That was before the SG brief (9/25) and before the GVR (11/9), so no outcome material existed to retrieve. `influenced_prediction` is `not_applicable` and `leakage_suspected` is false. The details are in `leakage.notes`.

**Semantic grades.** None: this is a cert cell with no declared semantic set.

**Big case (my read, 0.5).** The question is important and recurring: *Turner* deference versus heightened scrutiny for sex-based jail policies. Twenty-three states filed as amici and the federal BOP has an interest. But the Court disposed of the petition by GVR and decided nothing itself, and the vehicle is a pleading-stage case with a preservation problem.

## Scores

- Prediction: `granted`, p = 0.70. `correct` = 0 and `brier_score` = 0.09. This is the best Brier of the three, because the probability was high and the outcome was in the grant family.

## Reasoning quality — 0.30

`reasoning.md` is a single paragraph. It anchors on the statpack's CVSG cut (29.4% granted + 5.5% GVR) and then doubles the figure to 0.70. It cites a "clean, mature circuit split (3-3)", the 23-state amicus brief, and the claim that "the conservative majority is highly likely to grant plenary review."

The jump is not argued:
- It never engages the brief in opposition's vehicle objections: petitioners conceded intermediate scrutiny below, the panel decided on party-presentation grounds, and the case is at the pleading stage.
- It does not weigh the SG's likely position.
- It does not consider the GVR route at all, even though the petition leaned on the *Fowler* vacatur in light of *Skrmetti*. That route is the one that actually materialized.

The high probability happened to land in the grant family, but the document's mechanism (a plenary grant to resolve the split) was the wrong one. The reasoning is thin, so most of the Brier advantage is luck of direction rather than analysis.

## Predicted reasoning — 0.15

Central claims, in the order the document weights them:
1. **Plenary review is "highly likely," and a GVR is "less probable."** This is the document's headline route call, and it failed outright.
2. **At least one further distribution after the SG files.** Borne out.
3. **A relist after that.** Not borne out: the petition was disposed of at its first post-SG conference.

The QP-scope claim and the dissent-from-denial claim were conditional on outcomes that did not occur, so they earn neither credit nor penalty. A specific central call failed, and what held was generic. That places the grade between the 0.0 and 0.25 anchors.
