# Evaluation: claude-baseline

## Outcome and mechanical scores

This is a cert-stage evaluation of prediction run `20261004T180949Z`. The supplied outcome records denial on October 13, 2026, with `actual_granted = 0`. The candidate predicted `denied`, so `correct = 1`. With grant probability 0.13, its Brier score is `(0.13 - 0)^2 = 0.0169`. This observation does not by itself determine long-run calibration.

The prediction's frozen `baseline` band, `sal-v4`, and Term 2026 leave baseline, basis, and skill to the harness. Any comparison should use the stamped segment base rate; no competing anchor is calculated here. Cert votes are unscored. The separate forecast document is context only, quantitative claim scoring remains mechanical, and no semantic grades apply.

## Reasoning quality: 0.79

The rationale gives substantive arguments on both sides. It identifies the explicit-preclusion question, the absence of an appellate split, the MCorp obstacle, and the Johnson hold request. Its accounts of consistent appellate decisions and the government's distinction of Johnson are supported by the provisioned opposition, especially printed pages 7–12; the hold request appears in the petition's pages 34–35. It correctly selects the reached-band population conceptually rather than treating the terminal no-relist population as its prospective baseline. It also candidly limits claims drawn from unavailable independent research.

Several upward adjustments are weaker than the core legal analysis. Professional representation and the government's decision to address a requested hold are not demonstrated likelihood-ratio evidence. The suggestion that the alleged underlying misconduct makes this a worse jurisdictional vehicle is plausible but underexplained, since the question is access to immediate review rather than whether the enforcement allegations are true. The rationale recognizes Johnson's different subject matter but still gives the hold/GVR route substantial weight without independently verified related-case materials or matched empirical support.

There is also an internal arithmetic gap in the rationale for the headline probability. It assigns roughly 0.08 to the hold/GVR route while giving a hold probability of about 0.25 and a conditional GVR probability of 0.40–0.45. Multiplying those stated factors yields 0.10–0.1125, not 0.08; adding the stated 0.05 plenary component yields 0.15–0.1625, not 0.13. The candidate may intend an additional discount or overlap, but does not state one. This is a coherence check on `reasoning.md`'s justification of its own headline number, not a grade of the separate claims block. The realized Brier still uses the submitted 0.13 unchanged.

The denial supports the modal label but reveals no substantive Supreme Court rationale. No credit or penalty is assigned for the separate forecast's date, relist, writing, or other ancillary predictions.

## Leakage assessment

The prediction and log are forward, dated October 4, before the October 13 resolution. All 22 calls have captured-result markers. The three CourtListener searches are recorded as throttled. The corpus queries seek cited authorities and a broad grants population; their logged document date is February 11, 2025, not this petition's eventual disposition. No logged query or prose passage shows the case's own outcome as already known. The forecast of an October 13 denial is phrased prospectively; its matching date is not independently evidence of leakage. Thus `retrieved_outcome_material = false`, influence is `not_applicable`, and `leakage_suspected = false`.

## Evidence scope

The assessment uses the supplied outcome, blinded candidate documents and log, the provisioned questions presented and selected petition/opposition passages, the October 13 snapshot, and the committed statpack's population-definition caption. No outside case facts or live corpus queries were used. The historical statpack calculation was not independently reproduced from the current pack.
