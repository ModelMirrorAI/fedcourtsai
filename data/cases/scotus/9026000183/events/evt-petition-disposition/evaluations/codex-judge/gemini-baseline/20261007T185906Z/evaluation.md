# Evaluation: gemini-baseline

## Record and quantitative scores

This is a cert-stage evaluation of the blinded prediction from run 20261004T201824Z, against the supplied outcome.json. The event records denial on October 5, 2026, with actual_granted = 0. The candidate predicted denied at P(any grant) = 0.11: correct = 1 and Brier = (0.11 - 0)^2 = 0.0121. This is an exact disposition-label match, not a merits judgment.

The baseline comes from the candidate's own frozen context: baseline band, sal-v4, Term 2026. The matching sal-v4 table in the committed metrics/statpack.md displays all 10 of its 10 Terms; only the nine strictly prior Terms, 2017–2025, are pooled. The 2026 row is excluded. The reached-rate/weighted-n pairs are 3.9%/1140, 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643, in descending Term order.

The rendered-table weighted sum is 637.385 over 12,720, so segment_base_rate = 0.0501088836477987 (approximately 5.0109%) and base_rate_basis = risk_set. Because the displayed percentages are rounded, 637.385 is a weighted calculation, not an observed integer grant count. No terminal-band rate or evaluator-cell band is substituted. The pack describes this as a denial-reweighted paid scored-segment live/historical slice, not a census. I use the committed artifact supplied to this cell, not a freshly queried corpus; I make no claim about current corpus-wide freshness.

Baseline Brier is 0.0025109002204286; Brier skill = 1 - 0.0121/baseline_Brier = -3.818988784004. The negative skill means that this correct denial call assigned more grant probability than the segment prior and therefore performed worse on this one denial. It is not a claim about aggregate predictor performance.

## Rationale quality

The rationale correctly treats denial as the dominant outcome, starts from an approximately appropriate 4–6% risk-set anchor, and identifies counsel quality, business-amici participation, and the Rule 23 question as potential reasons for an upward update. It retains substantial uncertainty rather than treating an important question as an automatic grant.

The analysis is nevertheless thin on the actual dispute. Its discussion of vehicle quality centers on denial of en banc review instead of explaining the interlocutory certification posture, deferential review, alternative common questions, or the opposition's uniform-policy answer to the asserted split. The provisioned opposition expressly develops those points (Introduction and printed pp. 26, 34–35). Saying that the Court's conservative majority frequently polices this area does not establish why this petition presents a certworthy conflict. The increase to 11% is understandable but not closely tied to an examination of competing arguments. The reasoning gives no substantial analysis of how the three-stage trial plan changes the vehicle assessment.

These strengths and omissions support reasoning_quality = 0.65. The score is for reasoning.md alone, not for the forecast document, its relist narrative, or the numerical claims block. A correct denial label does not establish that the Court accepted this rationale.

## Leakage assessment

The log records 31 calls, all with result_capture = unobserved and aggregate coverage 0.0. This is a capture limitation, not a defect or proof that calls returned nothing. In particular, the retrieval note says the general corpus-priors command failed, but the log cannot independently establish that failure. Its query is about Rule 23 and uses a prior-Term filter, not this petition's disposition. The candidate's created_at precedes its logged tool calls, but both timestamps are on October 4 and before the recorded October 5 resolution; that discrepancy does not change the timing assessment. Nothing in the visible queries or reasoning shows an already-decided petition being forecast forward.

Accordingly, mode = forward, retrieved_outcome_material = false on the available evidence, influenced_prediction = not_applicable, and leakage_suspected = false. The candidate's own frozen mode and captured log govern; this evaluator's October 5 record context is not substituted for the prediction's baseline.

## Scoring boundaries

I read both reasoning.md and the pointer-named predicted_reasoning.md, but grade only the former for reasoning_quality. The realized record also notes a dissent from denial; the quantitative claim covering that fact, along with the remaining mechanical claims, is left to the harness rather than folded into rationale quality. No claim_scores, semantic_grades, vote_accuracy, or merits judgment score is written: this is a cert cell, and cert votes are not scored. The supplied outcome does not provide a merits opinion or establish the Court's reasons for denial. No optional independent big-case assessment is supplied. Process, context, prediction-run, and base-rate-version stamps are left to the harness.
