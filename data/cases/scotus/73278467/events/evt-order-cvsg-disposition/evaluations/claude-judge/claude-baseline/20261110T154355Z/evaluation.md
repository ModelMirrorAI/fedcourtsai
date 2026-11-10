# claude-baseline — evaluation

## Outcome

Cert-stage cell (moment `cvsg`). After the June 30, 2026 CVSG, the Solicitor General filed on September 25, 2026, recommending that the Court grant, vacate, and remand in light of *West Virginia v. B.P.J.* and *United States v. Skrmetti*. The petition was distributed on October 14 for the November 6 conference, and on November 9, 2026 the Court entered a GVR "in light of *West Virginia* v. *B. P. J.* … and *United States* v. *Skrmetti*." So `actual_disposition` is `gvr` and `actual_granted` is 1.

Every candidate scores `correct` = 0: no candidate predicted `gvr`, and `granted` and `gvr` are distinct labels. `brier_score` is `(p − 1)²`. The anchor (`segment_base_rate`, `brier_skill_score`, `base_rate_basis`) is left to the harness. Each prediction froze `band: high` under `sal-v4`, so the anchor is the stamped segment base rate over that risk set. I quote no rate of my own.

**Leakage.** Every candidate ran forward on 2026-09-18. That was before the SG brief (9/25) and before the GVR (11/9), so no outcome material existed to retrieve. `influenced_prediction` is `not_applicable` and `leakage_suspected` is false. The details are in `leakage.notes`.

**Semantic grades.** None: this is a cert cell with no declared semantic set.

**Big case (my read, 0.5).** The question is important and recurring: *Turner* deference versus heightened scrutiny for sex-based jail policies. Twenty-three states filed as amici and the federal BOP has an interest. But the Court disposed of the petition by GVR and decided nothing itself, and the vehicle is a pleading-stage case with a preservation problem.

## Scores

- Prediction: `granted`, p = 0.52. `correct` = 0 and `brier_score` = 0.2304.

## Reasoning quality — 0.50

`reasoning.md` is a careful, well-sourced document. It:
- anchors on the high band and the CVSG cut, both about 0.35;
- reads the June 30 CVSG, issued the same day *B.P.J.* came down, as a stronger interest signal than an ordinary CVSG;
- predicts the SG would align with petitioners (about 0.6 that the SG recommends grant or GVR). That held: the SG recommended a GVR;
- treats the vehicle problems seriously: the concession of intermediate scrutiny, party presentation, the Rule 12(b)(6) posture, and the unattractive facts on QP2.

Its pivotal analytical step was wrong, though. It argued that the Court "passed on a GVR when it was cheapest" and that *B.P.J.* "does not undercut" the Tenth Circuit. On that basis it put the summary route at only 0.12 conditional on a grant. The Court GVR'd expressly in light of *B.P.J.* and *Skrmetti*, which is exactly what the SG asked for.

The document saw the *Fowler*/*Skrmetti* GVR path only as a residual. It misread the CVSG as a step toward plenary review, when it was in fact a request for help on the GVR question. The probability lands near a coin flip, so the strong case analysis gets a middling grade because its central inference failed.

## Predicted reasoning — 0.25

Central claims, in order:
1. **A grant, most likely plenary on QP1.** Only the binary "some grant" held; the plenary form did not.
2. **Plenary review, not a summary disposition, with a GVR in light of *B.P.J.* explicitly rejected.** This is specific, and it failed: the GVR was entered in light of *B.P.J.*
3. **The SG supports petitioners and leans toward recommending a grant.** Borne out, although the SG asked for a GVR rather than plenary review.
4. **Further distribution near-certain.** Borne out.
5. **Timing: SG brief around December 2026, disposition January–March 2027 after one relist.** Not borne out: the SG filed in September and the Court disposed of the petition at its first post-SG conference.

The document is specific throughout, but its central route call failed. One secondary SG claim held. That fits the 0.25 anchor.
