# Evaluation — codex-baseline

**Cell.** Cert stage, forward mode. Johnson v. Montana, No. 25-1273 (Confrontation Clause: whether *Maryland v. Craig* or *Crawford* governs two-way video testimony by an adult prosecution witness). Outcome: `denied` on 2026-10-13 after two distributions, no CVSG, no noted dissent from denial. The prediction froze band `baseline` under `sal-v4`, so the segment base rate, `brier_skill_score` and `base_rate_basis` are stamped by the harness from the risk-set pool; I wrote none of them and compare against "the stamped segment base rate" only. `vote_accuracy` is omitted (cert cell). No `semantic_grades` (cert cell; no semantic set declared). Claims are scored in code and not graded here.

**Scores.** Predicted `denied`, P(grant) = 0.25 → `correct` = 1, Brier = 0.0625.

**Reasoning quality: 0.78.** Careful and well-sourced. Correct anchor (bracketed `reached`, `baseline`, eight Terms strictly before 2025, ≈5.12%, n ≈ 11,580), with an explicit note that terminal relist/CVSG cuts are not forward hazards. It read the BIO and reply with page cites, weighed preservation, invited error and harmlessness against the reply's answers, and read *Pitts v. Mississippi* directly — correcting the reply's characterisation of its facts (a physical screen, not one-way video), which is good independent checking. Its weakness is calibration of the net: it treats the vehicle objections as "not established defects" and lands at 25%, fivefold the anchor, on a split it itself shows is two state high courts against the field — the denial is better explained by the counterweights it listed than by the uplift it chose. Secondary probabilities are openly judgmental.

**Leakage.** Forward; `not_applicable`. Retrieval was pre-decision filings from snapshot-listed URLs and a 2025 precedent. Two web-open rows are `unobserved`; graded on their query (the BIO URL), which is pre-decision. A `find … -not -path 'data/qp-topics/*'` excluded that tree and is not a read.

**Big case (my read, 0.45).** Real doctrinal reach, weak vehicle, silent denial.
