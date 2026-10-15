# Evaluation: codex-baseline

## Outcome and reasoning quality

The predicted label, denied, matches the recorded outcome: correct = 1.
The grant probability was 0.42, giving (0.42 - 0)^2 = 0.1764.
Reasoning quality: **0.88**.

The rationale carefully separates the surcharge conflict from the suitability
of this petition. It addresses competing readings of the equitable-remedies
precedents, the top-hat-plan exemption, the disputed fiduciary relationship,
and the absence of an established liability predicate. Its distinction between
an unresolved threshold question and an independent lower-court holding is
supported by the supplied appellate passage, which expressly bypasses liability.
It fairly presents petitioners' trust-based response and explains why the
preemption question is a weaker independent route to review.

The empirical discussion recognizes the difference between a prior-conditioned
anchor and terminal descriptive cuts, and avoids counting CVSG interest twice.
The chief limitation is the modest upward adjustment to 0.42: the rationale
identifies both a developed conflict and substantial vehicle difficulties, but
the size and direction of the net adjustment remain subjective. It expressly
limits itself to the frozen record and does not infer an absent SG position.
Not retrieving additional permissible forward material is not itself an error.
Its larger Brier loss than the other forecasts is reported separately, not
used as a shortcut to discount otherwise substantial legal analysis. The
unexplained denial cannot resolve which of its doctrinal arguments was right.

## Leakage assessment

Forward mode; retrieved_outcome_material = false;
influenced_prediction = not_applicable; leakage_suspected = false.
The 34-call log has 31 captured results and three unobserved web calls.
Those three target general Amara precedent material; their unobserved markers
do not prove the reported empty responses. Other visible retrieval concerns
pre-existing precedents, supplied filings, and the statpack. The file-name
search excluding data/qp-topics entries is not a content read of that directory.
No query or rationale identifies this petition's disposing order. All logged
activity precedes the October 13, 2026 resolution; nothing indicates that an
already-decided case was provisioned forward. The April 7 cutoff bounds the
baseline, not an unrestricted forward retrieval clock.

## Scoring scope and baseline

This is a cert-stage evaluation. The committed outcome records denial on
October 13, 2026, with actual_granted = 0. Correctness compares the exact
outcome labels; the Brier score uses the probability of any grant. The denial
contains no explanation establishing why the Court declined review, so agreement
with the result does not verify any proposed doctrinal or vehicle explanation.

The prediction froze a high band under sal-v4 for OT2025. The stamped segment
base rate and associated skill are the harness's responsibility; I leave both
and base_rate_basis null and do not independently pool or quote a baseline.
Reasoning quality assesses reasoning.md only. The forecast document was read
for context but not scored; quantitative claims remain for the harness.
Cert votes and semantic claims are not graded on this stage.
