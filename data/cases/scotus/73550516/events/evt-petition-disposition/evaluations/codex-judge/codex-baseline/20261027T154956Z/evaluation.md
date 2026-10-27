# Evaluation: codex-baseline

## Outcome and quantitative assessment

This is a cert-stage event. The supplied outcome is **dismissed**, resolved October 20, 2026, with `actual_granted = 0`. The October 26 snapshot records an October 19 joint dismissal stipulation and an October 20 Rule 46 dismissal, not a cert denial or an adjudication of the governing-law question.

The predicted label **denied** is therefore wrong: `correct = 0`. The grant-family probability 0.24 produces `(0.24 - 0)^2 = 0.0576`. Favoring a non-grant does not satisfy exact disposition accuracy. Cert-stage vote accuracy is omitted.

The scored prediction froze `baseline`, `sal-v4`, Term 2025. Its **stamped segment base rate** and derived skill belong to the harness; no competing rate, basis assignment, or skill is recorded. Mechanical claims and the forecast document remain unscored here. There is no cert-stage semantic grading.

## Reasoning quality: 0.88

The rationale carefully separates the petition's alleged circuit conflict from what its historical authorities actually establish. It explains the GE Energy reservation, qualifies Setty's applicability, and examines the contract-language and state-law obstacles rather than adopting the petition's account wholesale. The hold request and unpublished follower decision support its conditional GVR analysis. It also distinguishes a requested response from four grant votes and explicitly refuses to infer a hold, denial, missed response, or substantive conference consideration from an incomplete snapshot.

Its main limitation is the substantial upward move to 0.24 without an empirically fitted conditional model or verified companion-case status. The missing opposition leaves preservation and vehicle objections unresolved. The reasoning would be stronger with an explicit voluntary-dismissal branch, but an October 20 stipulated exit is not proof that its doctrinal discussion was unsound. This high quality grade reflects evidentiary discipline and balanced analysis, not correctness of the outcome label, the forecast document, or any mechanical claim.

## Leakage

The log is **forward** and contains 42 calls: 39 captured and three unobserved. The three unobserved web calls concern historical GE Energy and Setty sources; their absent results are not credited as failed or empty retrieval. The captured operational and historical-research calls and the staged prose show no retrieval of this petition's disposing material. Research and prediction on October 6 preceded the October 19 stipulation and October 20 dismissal. Influence is `not_applicable`, `retrieved_outcome_material = false`, and `leakage_suspected = false`.

Only provisioned evidence was used for this evaluation; no external case facts were retrieved.
