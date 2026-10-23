# codex-baseline — scotus/9526000416 evt-motion-disposition

## Cell

**Interim** cell: application 26A416, *Trump v. Kingdom*. The SG asked for a stay of the district court's classwide preliminary injunction against the BOP gender-dysphoria policy. **Outcome:** the application was referred to the Court on 2026-10-21 and **denied**, with Justices Thomas and Alito noting they would grant. This was an outright denial. It was not a partial grant that the resolver collapsed to denied. `actual_granted` = 0.

The harness stamps the baseline (the substantive-application grant rate pooled over application-Terms before 2026) and the Brier skill score. I write neither here and quote no rate of my own. If the stamped rate comes back null, the pool fell below its registered floor or the pack lacked the interim section. The pooled population the candidates cite (2024–2025) is above the 50-resolved floor, so I expect a stamped value. `claim_scores` (interim-v1) is the harness's. No semantic set is declared on an interim cell, so there is no `semantic_grades` block. Vote blocks go unscored at this stage.

**Leakage:** this is a forward cell, with prediction cutoff 2026-09-29 and resolution 2026-10-21. `not_applicable` was confirmed against the log (see `leakage.notes`).

## Score

Predicted `granted` at P=0.68. **correct = 0**, **Brier = 0.4624**.

## Reasoning quality: 0.50

Strengths: a careful information-set statement, and a correctly pooled strictly-prior anchor (31/296) with honest coverage caveats. The candidate also took the contrary evidence seriously, and that evidence is what carried the day. It names the D.C. Circuit majority's ground (BOP failed to address its own experience under the prior policy). It notes that a long administrative record does not cure an omitted explanation. It names the inmates' continuity-of-care harm and the status-quo character of the injunction. It splits the remaining probability explicitly: 0.17 outright denial and 0.14 partial relief.

Weakness: the leap from a 10.5% anchor to 0.68 rests on a judgmental reading of applicant class and stakes, with no measured comparator. Having laid out the countervailing record-based APA case, it still weighted the government's remedial-overbreadth and PLRA routes heavily. The Court did not take them, and four Justices beyond the noted pair declined to intervene. The analysis was sound in structure but miscalibrated in its conclusion.

