# Evaluation: codex-baseline

## Scope and ground truth

This is a cert-stage evaluation. The provisioned outcome records `gvr`,
`actual_granted = 1`, resolved October 13, 2026. The October 13 snapshot
independently contains the order granting the petition, vacating the judgment,
and remanding in light of Durnell. This is not a plenary grant or a merits
judgment. The outcome establishes that disposition, not a new merits holding.

All candidates froze an elevated band under sal-v4. The stamped segment base
rate and its derived skill are the harness's; I leave `segment_base_rate`,
`brier_skill_score`, and `base_rate_basis` null and do not compute a competing
anchor. No terminal fallback applies. I did not independently audit the
historical statpack figures quoted in the candidates' rationales.

Only `reasoning.md` contributes to reasoning quality. The separate forecast
was read for context, not graded; quantitative claims remain for the harness.
No semantic set is graded on this cert cell, and cert votes are not scored.
The stakes assessment is the same independent case assessment for every
candidate: a substantial individual judgment and broader litigation relevance,
but a requested follow-on remand rather than a new doctrinal decision.

## Outcome and reasoning quality

The predicted label `gvr` exactly matches: `correct = 1`. With P(any grant)
0.97 and actual grant 1, Brier = (0.97 - 1)^2 = **0.0009**.

**Reasoning quality: 0.94.** The rationale directly identifies the strongest
record evidence: respondent's September 2 response expressly does not oppose
the requested GVR and confirms the label-based character of the judgment.
It distinguishes that concession from an ordinary opposition, distinguishes
GVR from plenary review, and explains why the rejected design-defect claims
reduce the apparent independent-ground concern. It correctly distinguishes
two distribution entries from a completed post-conference relist. Its
baseline discussion separates a prior-Term risk-set anchor from terminal
population descriptions rather than treating those descriptions as forward
hazards. These are strengths of the analysis, not rewards for a correct result.

The residual allowance for jurisdiction, preservation, and record uncertainty
is explicit, and the candidate discloses that its account of the companion
decision comes from the parties rather than an independently read opinion.
The exact 97% remains judgmental, not established by a matched empirical
sample; the appendix was not independently audited. Those limitations keep
the score below perfect without treating the successful forecast as proof
that its precise probability was calibrated.

## Leakage assessment

The log identifies a forward run on September 27, 2026, before the October 13
resolution. Its 26 calls include 24 captured results and two unobserved web
searches, both about general Lawrence v. Chater/GVR practice, not this case.
Although the prose says those searches returned no usable results, the log
cannot verify their contents; null dates on unobserved calls are not evidence
of an empty result. Their query content presents no own-case outcome signal.
The remaining queries concern provisioned filings and snapshot, aggregate
statpack context, and local operational tasks. The excluded-path `find` is
not a read of topic-label artifacts. Nothing in the visible log or rationale
shows this petition's disposition already known. The June companion decision
and September response are pre-resolution forward information, not leakage.

`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
and `leakage_suspected = false`, on the observable record rather than on an
assumption that uncaptured results were empty. The predictor's September 27
snapshot itself is not staged here; the evaluator's later snapshot is not
substituted for it in this assessment.
