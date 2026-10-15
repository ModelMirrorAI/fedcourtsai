# Evaluation: codex-baseline

## Outcome and quantitative score

The cert-stage ground truth is `denied` on October 13, 2026, with
`actual_granted = 0`. The provisioned October 13 snapshot corroborates the
outcome file. codex-baseline predicted denial and assigned a 0.06 grant
probability: `correct = 1`, and `(0.06 - 0)^2 = 0.0036` is the Brier score.
The denial resolves the forecasted disposition, not the competing statutory
interpretations discussed in the rationale.

The prediction carries a frozen baseline band under sal-v4 and Term 2025.
The stamped segment base rate, basis, and Brier skill are harness-owned, so
I write none of them and supply no separately pooled comparator. No cert vote
accuracy or semantic grades are appropriate. I read `predicted_reasoning.md`
for context but do not score it or the quantitative claims block.

## Reasoning quality: 0.88

The rationale carefully separates facts, inferences, and missing information.
It treats four response extensions as extensions rather than relists, does
not confuse a federal respondent with a federal petitioner, and distinguishes
the filing of an opposition from knowledge of its arguments. Its described
baseline method matches the frozen-band, strictly-prior-Term approach; it
acknowledges rounded rates, population differences, and unavailable freshness
metadata rather than presenting the anchor as exact or freshly measured.
I assess that methodological explanation without recomputing the baseline.

The legal analysis is focused on the cert decision: it identifies the
distinction between discretionary relief and antecedent eligibility findings,
describes the lower court's extension of precedent, and recognizes that an
unresolved issue does not itself establish an inter-circuit conflict. Missing
petition and opposition texts, unverified split allegations, and uncertain
vehicle quality are treated as limits on inference rather than negative facts.
The small upward adjustment is explained as a judgment about issue significance,
not as a mechanically estimated rate.

The remaining limitations are meaningful but explicit. The analysis largely
relies on the underlying appellate opinion's account of the authorities, does
not independently resolve the contemporary circuit landscape, and cannot
evaluate the petition's actual question presented or preservation. The precise
adjustment to 0.06 remains judgmental. These prevent a near-perfect soundness
score but do not undermine the central, well-qualified denial analysis. The
score does not reward the separate document's timing or procedural predictions.

## Leakage assessment

All 26 calls in the forward-mode log occurred on October 3, before the October
13 disposition. The external case-specific search is restricted to the
underlying Eighth Circuit judgment filed before January 10, 2026, followed by
reads of that opinion. The remaining visible queries concern local inputs,
statistical context, and general Supreme Court rules. No query or reasoning
shows this petition's later denial being sought or treated as known.

Capture coverage is 24 of 26 calls. The two unobserved web calls concern
general certiorari rules and a rules PDF. I do not treat the candidate's
description of empty results, or the log's null document dates, as captured
proof that those calls returned nothing; their query scope and pre-resolution
timing are the relevant evidence. Influence is `not_applicable`, retrieved
outcome material is false on this record, and leakage suspicion is false.
