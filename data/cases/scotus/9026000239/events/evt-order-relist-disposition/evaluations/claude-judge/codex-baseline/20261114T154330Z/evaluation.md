# Evaluation: codex-baseline

**Outcome.** Certiorari granted on 2026-11-13, plenary route, limited to Questions 1 and 2. The prediction named `granted` at P = 0.90.

- `correct` = 1 (label `granted` matches `actual_disposition`).
- `brier_score` = (0.90 - 1)^2 = 0.01.
- This is a cert-stage cell: no vote accuracy, no semantic grades. The segment base rate, skill score and claim scores are the harness's to stamp.

## Reasoning (`reasoning_quality` 0.8)

This is the most careful rationale of the three on method. It reproduces the frozen federal anchor from the statpack counts (155/212) and says explicitly that the federal caption class is already in that anchor, so government petitioning is not counted twice. It treats the relist, CVSG and amicus tables as mixed-caption terminal cuts rather than likelihood ratios, and it notes that the terminal one-relist bucket is not the hazard a petition at its first relist faces. It records correctly that the petition file is truncated and that the docket shows four amicus briefs despite the null context field.

On substance it engages both sides: the opposition's Chenery, unchallenged-vacatur and 1252(f)(1) arguments, the reply's answers, and the panel dissent. It identifies D.V.D. from the reply as the real alternative path and is disciplined about what it could and could not verify about that case.

What holds it short of the top: it gave the D.V.D. hold-and-GVR path a quarter of the mass (25% GVR in its illustrative allocation) and a 46% chance of a further distribution, while its own analysis had already concluded that D.V.D. does not reach the central asylum question. The Court granted at the first post-relist conference on Questions 1 and 2. The headline number was well placed; the route and timing weights were too cautious for the evidence it had laid out.

## Predicted reasoning (`predicted_reasoning_quality` 0.45)

I treated five claims as central: the plenary grant, the further-distribution call, Question 1's asylum component, the lean on Questions 2 and 3, and the 30% summary-route weight.

The direction was right: a plenary grant, no further distribution as the modal call, Question 1 taken. But the document committed to little beyond the outcome. Its timing forecast spans zero to two more relists, action in November or December, or a hold into 2027, which almost no outcome could contradict.

Where it did discriminate, it leaned the wrong way. It said the Court "may also take" Question 3 and described Question 2 as the one most likely to be handled through D.V.D. The order took Question 2 and dropped Question 3. It also put 30% on a cert-order disposition conditional on a grant, a weight the prompt outcome did not bear out, though plenary remained its modal route.

That is a right-in-direction forecast, mostly generic, with its one specific secondary call missed. I placed it just under the 0.5 anchor.

The denial-conditional content never came into play and earns neither credit nor penalty.

## Leakage

Forward cell, made on 2026-11-09 while the petition was pending. Web rows were uncaptured, so I graded them on their queries: general precedent PDFs and the docket of a different case (D.V.D.). No call sought this petition's docket or outcome. Graded `not_applicable`.

## Big case

My read is 0.9: a presidential proclamation suspending asylum access at the southern border, nationwide classwide relief, and a recurring 1252(f)(1) question, now set for plenary review.
