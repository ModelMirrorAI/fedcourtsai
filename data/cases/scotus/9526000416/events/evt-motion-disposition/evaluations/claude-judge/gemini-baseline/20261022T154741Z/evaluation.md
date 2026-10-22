# gemini-baseline — scotus/9526000416 evt-motion-disposition

## Cell

**Interim** cell: application 26A416, *Trump v. Kingdom*. The SG asked for a stay of the district court's classwide preliminary injunction against the BOP gender-dysphoria policy. **Outcome:** the application was referred to the Court on 2026-10-21 and **denied**, with Justices Thomas and Alito noting they would grant. This was an outright denial. It was not a partial grant that the resolver collapsed to denied. `actual_granted` = 0.

The harness stamps the baseline (the substantive-application grant rate pooled over application-Terms before 2026) and the Brier skill score. I write neither here and quote no rate of my own. If the stamped rate comes back null, the pool fell below its registered floor or the pack lacked the interim section. The pooled population the candidates cite (2024–2025) is above the 50-resolved floor, so I expect a stamped value. `claim_scores` (interim-v1) is the harness's. No semantic set is declared on an interim cell, so there is no `semantic_grades` block. Vote blocks go unscored at this stage.

**Leakage:** this is a forward cell, with prediction cutoff 2026-09-29 and resolution 2026-10-21. `not_applicable` was confirmed against the log (see `leakage.notes`).

## Score

Predicted `granted` at P=0.75. **correct = 0**, **Brier = 0.5625**.

## Reasoning quality: 0.25

The candidate correctly identified the ~10.5% strictly-prior anchor. The rest of the rationale is generic. It states that the Court is "historically very receptive" to SG stay applications against nationwide injunctions, with no comparator, no case-specific engagement and no analogue. It acknowledges that the APA claims might be strong, but does not examine the D.C. Circuit's record-based ground, the district court's findings, or the medical harm to the class. It gives no decomposition between outright denial and partial relief. It assigned the highest probability of the three on the thinnest analysis, and the outcome (a denial in which only two Justices noted a grant) contradicts its central premise that the posture "heavily favors a stay".

