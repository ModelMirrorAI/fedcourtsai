# Evaluation — codex-baseline

## Cell

Interim stage (stay-vacatur application, arrival moment). Outcome: `denied`, `actual_granted` = 0, resolved 2026-10-26. The baseline and skill (`segment_base_rate`, `brier_skill_score`) are the harness's to stamp from the statpack's interim section, so this evaluation writes neither and leaves `base_rate_basis` null; refer to "the stamped segment base rate". The prediction froze no band (`context.band` null), the ordinary interim shape. No votes are scored on an interim cell, no semantic set is declared, and `claim_scores` is the harness's.

## Score

Predicted `denied` at P(grant) = 0.27 → `correct` = 1, Brier = 0.0729.

## Reasoning quality: 0.70

Careful and well-sourced: correct anchor (53/549 = 9.65%) with an honest discussion of uneven historical parsing; reads the whole application and correctly notes the Fourth Circuit decision is not a square post-transmittal holding; states the governing vacatur standard (*Western Airlines*/*Coleman v. Paccar*: demonstrably wrong plus serious irreparable injury) and uses *Coinbase* sensibly as a reason the Fifth Circuit's position is defensible. Its own downward considerations (demanding standard, delay-type harm, alternative *Brunswick* vehicle, recusal) are persuasive, yet it nearly triples the anchor to 0.27 on the strength of "a developed legal dispute" — an upward adjustment the analysis does not really earn, and it under-weights the pending *Brunswick* petition as the Court's likely route. Direction right, calibration loose.

## Leakage

Forward, `not_applicable`. CourtListener and web calls targeted only general precedent (1976–2023); three web rows are `unobserved` and graded on their queries, none naming this case. No outcome material.
