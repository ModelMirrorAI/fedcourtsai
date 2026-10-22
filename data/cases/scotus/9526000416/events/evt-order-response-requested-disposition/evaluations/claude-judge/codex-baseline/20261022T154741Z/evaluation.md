# Evaluation: codex-baseline, Trump v. Kingdom (26A416), response-requested disposition

**Stage: interim.** The SG applied to stay the D.D.C.'s renewed class-wide PLRA preliminary injunction / § 705 stay against BOP's February 2026 gender-dysphoria policy. **Outcome: denied** on 2026-10-21 after referral to the Court. Only Justices Thomas and Alito noted they would grant. `actual_granted` = 0.

- `correct` = 0 (predicted `granted` vs actual `denied`).
- `brier_score` = 0.4624 (P = 0.68).
- Baseline and skill: this is an interim cell, so `segment_base_rate`, `brier_skill_score` and `base_rate_basis` come from the harness's `stamp-cell` (the substantive-application grant rate, pooled over application-Terms strictly before 2026). I wrote none of them. If the stamped rate comes back null, that means the pool fell below its registered floor or the pack lacked the section; a null field does not say which. No band was frozen, which is the normal shape for an application.
- `vote_accuracy` is not scored on an interim cell. `claim_scores` (interim-v1) is the harness's. No semantic set is declared, so there is no `semantic_grades` block.
- **Leakage:** forward cell, predicted 2026-09-29, three weeks before resolution. No outcome material was retrieved, so the grade is `not_applicable`. Details are in `leakage.notes`.

## Reasoning quality: 0.6

This is the most self-critical of the analyses. It anchors correctly on the committed 31/296 pool and declines to infer conditional rates from the escalation columns. It checks the general stay, APA and PLRA standards against primary authority. It treats the application's factual assertions as advocacy rather than established findings. The "Why not a near-certain grant" section names the considerations most consistent with the actual denial. Those are existing-care reliance and patient-specific irreparable harm, the circuit majority's view that a long record is not an adequate explanation, and delay weakening the emergency showing. Still, it put only 0.15 on outright denial, and it still landed at 0.68 for an unqualified grant without stating what moved it so far above the anchor beyond "review-worthy stakes." It is better calibrated in substance than in its number.
