# Evaluation: codex-baseline

## Outcome and numerical score

This cert-stage evaluation targets prediction run `20260917T214606Z`.
The supplied outcome is denial on October 13, 2026, with binary outcome
zero. The predicted `denied` label matches: `correct = 1`. Its Brier
score is `(0.10 - 0)^2 = 0.01`.

The prediction freezes elevated, sal-v4, Term 2025. The harness supplies
the segment baseline, basis, and skill; any comparison should use the
stamped segment base rate. No alternative evaluator rate is calculated.
Votes are not scored on cert, no semantic set is declared, and mechanical
claims are left for the harness.

## Reasoning quality: 0.90

The rationale carefully distinguishes a future scheduled conference from
completed consideration. It keeps the frozen band intact while explaining
why a redistribution after the requested response may warrant a downward
adjustment within that band. It also separates contextual statistical
cuts from independent likelihood ratios and describes the numerical
adjustment as judgmental rather than fitted. Its stated historical anchor
excludes the prediction's own Term, and its publication-vintage caveat
avoids presenting a commit date as corpus freshness.

The case-specific analysis is well grounded in the supplied advocacy:
the petition's causation formulations purportedly yield the same result,
the appellate court declined to reach causation/materiality, and the
opposition frames the surviving claim around deliberate evasion of
verification. The rationale treats that opposition account as advocacy,
not an established finding, while preserving petitioner's immunity-specificity
argument as a nontrivial contrary consideration. These distinctions explain
the probability rather than simply rationalizing a denial label.

Limitations remain. The precise adjustment to ten percent lacks a measured
response-request/rescheduling comparison group, which the candidate admits.
Its selected-page opposition review and omission of the reply leave part of
the adversarial exchange untested. The supplied reply disputes the verifier's
retirement chronology and argues that causation belongs within the immunity
appeal; those points matter to assessing how confidently the opposition's
vehicle framing should be accepted. The rationale's explicit caution and
limited factual commitments mitigate, but do not eliminate, that gap.

The grade evaluates only the analysis in `reasoning.md`, not the separate
forecast or quantitative claims. The recorded denial confirms the label,
not any particular proposed judicial rationale.

## Leakage and evidence limits

The harness log marks forward mode. It captures 25 of 28 results; the three
unobserved calls are two exact-URL opposition requests and an authority
search using Zorn/Lalli. The candidate reports no useful output from those
calls, but the telemetry cannot independently establish that. Their query
scope does not seek this petition's eventual disposition. Captured calls
subsequently extract the August 31 opposition, a pre-decision filing.

All this retrieval precedes the October 13 denial, and neither the query
record nor the rationale shows the case already decided when predicted.
No outcome material is evidenced; influence is `not_applicable`, with no
leakage suspected. This does not treat unobserved results as empty.

The independent case-significance assessment reflects the questions and
interlocutory posture rather than the candidate's own numerical assessment.
