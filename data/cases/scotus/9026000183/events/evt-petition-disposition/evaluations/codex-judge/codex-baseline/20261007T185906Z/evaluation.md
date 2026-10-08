# Evaluation: codex-baseline

## Record and quantitative scores

This is a cert-stage evaluation of the blinded prediction from run 20261004T201824Z, against the supplied outcome.json. The event records denial on October 5, 2026, with actual_granted = 0. The candidate predicted denied at P(any grant) = 0.12: correct = 1 and Brier = (0.12 - 0)^2 = 0.0144. This is an exact disposition-label match, not a merits judgment.

The baseline comes from the candidate's own frozen context: baseline band, sal-v4, Term 2026. The matching sal-v4 table in the committed metrics/statpack.md displays all 10 of its 10 Terms; only the nine strictly prior Terms, 2017–2025, are pooled. The 2026 row is excluded. The reached-rate/weighted-n pairs are 3.9%/1140, 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643, in descending Term order.

The rendered-table weighted sum is 637.385 over 12,720, so segment_base_rate = 0.0501088836477987 (approximately 5.0109%) and base_rate_basis = risk_set. Because the displayed percentages are rounded, 637.385 is a weighted calculation, not an observed integer grant count. No terminal-band rate or evaluator-cell band is substituted. The pack describes this as a denial-reweighted paid scored-segment live/historical slice, not a census. I use the committed artifact supplied to this cell, not a freshly queried corpus; I make no claim about current corpus-wide freshness.

Baseline Brier is 0.0025109002204286; Brier skill = 1 - 0.0144/baseline_Brier = -4.734994916501. The negative skill means that this correct denial call assigned more grant probability than the segment prior and therefore performed worse on this one denial. It is not a claim about aggregate predictor performance.

## Rationale quality

The rationale develops both sides of the certification dispute rather than inferring certworthiness from the caption or amici alone. It separates common proof from similar individualized evidence, explains the opposition's uniform-policy distinction, identifies alternative common questions, and recognizes that Judge Willett concurred in the judgment. The provisioned opposition corroborates the concurrence and alternative-common-question discussion (printed pp. 12 and 26), and expressly develops the provisional certification and trial-management objections (printed pp. 34–35).

It also distinguishes an interlocutory vehicle discount from a categorical bar to Rule 23 review, treats the competing briefs as advocacy, and does not infer a hold merely from the snapshot's lack of a later entry. Its account of the older Tyson Foods check is appropriately limited: separately tried issues can coexist with predominating common issues, not that the precedent automatically resolves this class's certification. The forecast's 12% is expressly a judgmental update, with the unreviewed reply and disputed split identified as uncertainty.

Reasoning_quality = 0.90 reflects that disciplined, case-specific analysis. The main limitation is the absence of a reproducible quantitative bridge from the roughly 5% prior to 12%; the upward adjustment remains a qualitative judgment. The denial supports the headline call but does not reveal the Court's reasons. The candidate's 638/12,720 anchor is its stated full-precision statpack calculation; this evaluation uses the contract's rendered-table calculation, whose slightly different result reflects rounding rather than a substantive baseline disagreement. Neither the forecast prose nor any claim probability contributes to this qualitative grade.

## Leakage assessment

The log contains 41 calls, with 37 captured and four unobserved (coverage 37/41 = 0.902439). The unobserved searches/opens concern general Supreme Court rules, not this case. Although the candidate reports no usable content from those calls, the capture markers establish only that their results are unavailable. The CourtListener queries concern old Wal-Mart, Halliburton, and Tyson Foods authorities, including opinion 3187537, not this petition's subsequent history. The statistical-artifact history query concerns metrics/statpack.md alone. No visible query or rationale supplies the October 5 denial in advance.

Accordingly, mode = forward, retrieved_outcome_material = false on the available evidence, influenced_prediction = not_applicable, and leakage_suspected = false. The candidate's own frozen mode and captured log govern; this evaluator's October 5 record context is not substituted for the prediction's baseline.

## Scoring boundaries

I read both reasoning.md and the pointer-named predicted_reasoning.md, but grade only the former for reasoning_quality. The realized record also notes a dissent from denial; the quantitative claim covering that fact, along with the remaining mechanical claims, is left to the harness rather than folded into rationale quality. No claim_scores, semantic_grades, vote_accuracy, or merits judgment score is written: this is a cert cell, and cert votes are not scored. The supplied outcome does not provide a merits opinion or establish the Court's reasons for denial. No optional independent big-case assessment is supplied. Process, context, prediction-run, and base-rate-version stamps are left to the harness.
