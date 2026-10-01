# Evaluation: claude-baseline

## Outcome and scores

This is an interim application, not a cert or merits event. The recorded outcome is denied, with actual_granted = 0, resolved September 29, 2026. The September 30 provisioned snapshot records Justice Sotomayor's denial without prejudice to renewed relief once state remedies are exhausted. claude-baseline predicted denied at P(unqualified grant) = 0.22: correct = 1 and Brier = (0.22 - 0)^2 = 0.0484.

## Reasoning quality: 0.84

The rationale identifies the decisive tension: a potentially substantial religious-autonomy/compelled-speech claim versus unexhausted state procedures and an undecided appellate stay motion. It differentiates the two challenged directives, recognizes the absence of an imminent contempt order, and uses the applicants' account of state proceedings to explain why denial remains more likely. The actual order expressly invoking exhaustion supports that central analysis; it does not establish that the constitutional claim lacked merit.

The prior-Term anchor and coverage caveat are transparent. The upward adjustment is nevertheless judgmental: a few recent application comparisons do not establish a response-requested conditional rate. Calling the response request the strongest rung overstates what the evidence establishes. The assertion that partial relief resolves as denial is also broader than the stated denial-first rule for expressly mixed orders. These analytical qualifications, rather than the correctness of the final label, keep the score below excellent. Comparator holdings were not independently re-retrieved in this evaluation.

Only reasoning.md is graded. Forecast prose, increment probabilities, referral expectations, timing and vote speculation are not folded into this score. The harness alone scores the quantitative claims.

## Baseline and scope

The interim baseline and skill are harness-owned and intentionally absent from evaluation.json; base_rate_basis is structurally null. The committed statpack shows 31 grants among 296 substantive resolutions in the strictly prior 2016–2025 window for the prediction's frozen application-Term 2026, clearing the pooled 50-resolution floor. These are artifact counts, not a claim about a freshly queried corpus. Coverage is uneven (972 unparsed applications in 2024); machine-matchable resolutions select the pool, withdrawals/dismissals are ungranted, and mixed orders read denial-first. The pool is not conditioned on response requests and is broader than the escalation-selected forecast population. No stamped baseline is available yet.

No vote accuracy or semantic grades are written on this interim cell. No independent big-case assessment was formed before seeing candidate scores, so that optional field is omitted.

## Leakage

Forward mode is corroborated by September 27 calls preceding the September 29 disposition. The log has 41 calls and full result-capture coverage, although result digests do not expose full returned text. Target-case searches and a live-docket fetch are visible; the disclosed September 25 amicus is ordinary forward information despite postdating the September 24 baseline cutoff. No call or reasoning shows the September 29 disposition as already known. Retrieved outcome material is false, influence is not_applicable, and leakage_suspected is false. The evaluator's later snapshot is not treated as the predictor's baseline.
