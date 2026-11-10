# Evaluation: codex-baseline

## Cell

Cert-stage cell (`stage: cert`, `moment: distribution`), forward mode. Outcome: **denied** on 2026-11-09 after a single distribution (Conference of 11/6/2026), following the Solicitor General's 2026-10-16 waiver; no response requested, no CVSG, no noted dissent. `correct` and `brier_score` below are my elicited reads; the harness stamps both, plus the segment base rate and skill (refer to "the stamped segment base rate"). No semantic set is declared on a cert cell, and votes are not scored at this stage.

## Leakage

Forward, predicted 2026-10-31, nine days before the denial. The retrieval log shows no query for this docket's disposition, no document dated on or after resolution, and no `data/qp-topics/` access. Graded `not_applicable`; `leakage_suspected: false`.

## Score

Predicted `denied`, P(grant) = 0.025. Correct; Brier = 0.000625.

## Reasoning quality: 0.74

The rationale is careful and well sourced. It uses the frozen anchor properly and labels the terminal-state relist and amicus buckets as associations rather than transition probabilities, which is good statistical hygiene. It checks *Moe* and *Fuqua* directly. It identifies the same real vehicle problems as its peers: the unpublished summary affirmance, the election not to seek a Labor determination, and Labor's memorandum on likely coverage. It also notes that *Moe* itself ruled for the government. The main weakness is calibration. It treats the SG's waiver with no call for response as only "modest negative attention evidence" and stops at 2.5%, roughly half the anchor. That is less movement than its own vehicle analysis supports for a waived, unrelisted, zero-amicus paid petition. The relist-increment of 10% is likewise generous for this posture. The analysis was sound and the call was correct, but its own reasoning supported a lower number than it settled on.

## Predicted reasoning: 0.60

Central claims: (1) denial after the first conference with zero additional distributions; (2) ~10% chance of a further distribution; (3) no CVSG; (4) no separate writing. All were borne out. The conditional narrowed QP and plenary route are unresolved. The document is accurate but slightly more hedged than its peers ("most likely"), and its forecast is the default for this posture. That places it a little below the other two.
