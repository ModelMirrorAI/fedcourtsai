# Evaluation — gemini-baseline

## Cell

Interim stage (stay-vacatur application, arrival moment). Outcome: `denied`, `actual_granted` = 0, resolved 2026-10-26. The baseline and skill (`segment_base_rate`, `brier_skill_score`) are the harness's to stamp from the statpack's interim section, so this evaluation writes neither and leaves `base_rate_basis` null; refer to "the stamped segment base rate". The prediction froze no band (`context.band` null), the ordinary interim shape. No votes are scored on an interim cell, no semantic set is declared, and `claim_scores` is the harness's.

## Score

Predicted `denied` at P(grant) = 0.35 → `correct` = 1, Brier = 0.1225.

## Reasoning quality: 0.40

Right anchor (9.65%), right direction, but thin and partly inaccurate. It describes a "mature 3-1 split" with the Fourth Circuit on the Fifth/Eleventh side, while the provisioned application itself says the Fourth Circuit "suggested, but technically not held" the point and calls the split 2-1 (if not 2-2). It says the split "practically guarantees" eventual review, without engaging the 2026 *Harrison* cert denial, and treats likely plenary review as raising the chance of emergency vacatur — the opposite of the more natural inference that a pending cert vehicle (*City of Brunswick*, which it does not mention) lowers it. The ~3.6× upward adjustment is asserted, not reasoned, and the vacatur standard is invoked only in passing. No discussion of the recusal.

## Leakage

Forward, `not_applicable`. All calls `unobserved` (coverage 0.0); graded on their queries, which read only the provisioned record and the statpack. No outcome material.
