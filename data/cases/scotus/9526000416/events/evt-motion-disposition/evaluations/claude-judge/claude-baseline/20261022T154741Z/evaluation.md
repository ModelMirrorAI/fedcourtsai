# claude-baseline — scotus/9526000416 evt-motion-disposition

## Cell

**Interim** cell: application 26A416, *Trump v. Kingdom*. The SG asked for a stay of the district court's classwide preliminary injunction against the BOP gender-dysphoria policy. **Outcome:** the application was referred to the Court on 2026-10-21 and **denied**, with Justices Thomas and Alito noting they would grant. This was an outright denial. It was not a partial grant that the resolver collapsed to denied. `actual_granted` = 0.

The harness stamps the baseline (the substantive-application grant rate pooled over application-Terms before 2026) and the Brier skill score. I write neither here and quote no rate of my own. If the stamped rate comes back null, the pool fell below its registered floor or the pack lacked the interim section. The pooled population the candidates cite (2024–2025) is above the 50-resolved floor, so I expect a stamped value. `claim_scores` (interim-v1) is the harness's. No semantic set is declared on an interim cell, so there is no `semantic_grades` block. Vote blocks go unscored at this stage.

**Leakage:** this is a forward cell, with prediction cutoff 2026-09-29 and resolution 2026-10-21. `not_applicable` was confirmed against the log (see `leakage.notes`).

## Score

Predicted `granted` at P=0.68. **correct = 0**, **Brier = 0.4624**.

## Reasoning quality: 0.50

Strengths: the richest research of the three. It found the correct anchor (31/296) and disclosed it. It drew the SG's corpus record from a disclosed sweep. It found the closest analogue (*Trump v. Orr*, same Executive Order, granted 6-3). Under adjustments down it named the factor that proved decisive: a fact-bound APA dispute on an eighteen-month record, about a policy already enjoined twice. The district court found pretext, and the D.C. Circuit's record-based ground is one Justices could accept without touching doctrine. It also flagged Roberts and Barrett as possible defectors and said the number might belong nearer 0.55.

Weakness: the forecast admittedly rests on applicant identity and the Orr analogue more than on this record. It discounted the very distinction (a redone record, plus pretext findings) that separated this case from Orr. The (unscored) vote block placed Roberts, Gorsuch, Kavanaugh and Barrett with the government, but only Thomas and Alito noted a grant. The structure of the analysis was good, but the weighting went the wrong way.

