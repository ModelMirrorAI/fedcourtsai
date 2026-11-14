# Evaluation: claude-baseline

## Outcome and quantitative score

This is a **cert** cell. The November 13, 2026 outcome is `granted`, with `actual_granted: 1` and a plenary route. The docket limits review to a reformulated Question 1 concerning materiality and the separate misleading-effect inquiry under Section 11(a). The predicted `granted` label is correct: **correct = 1**. With P(grant) = 0.52, **Brier = (0.52 - 1)^2 = 0.2304**. No cert votes are scored; there is no merits judgment or semantic grading.

## Rationale quality: 0.80

`reasoning.md` gives a coherent conditional model of the government's recommendation, distinguishes grant from merits success, and weighs remand posture and the opposition's characterization objection. It correctly treats the first-conference CVSG, industry interest, and statutory distinction as reasons for serious review, without pretending to possess the later SG filing. Its candid uncertainty about the current docket is appropriate.

The weaker steps are the unsupported extra premium for an immediate CVSG, possible overlap between that signal and the already-high attention band, and a speculative inference from regulatory preferences to an SG recommendation. Assertions about the strength of both circuit conflicts exceed the document's treatment of the opposition. The approximate SG-adherence statistic is not substantiated in the staged record. These limitations, not the forecast document's timing or question-selection errors, keep the rationale below the top tier.

Historical base-rate use was checked against statpack build `73762050f49cd68912e89c864e25a792e498b45a`, landed September 14, 2026, recovered by `statpack-at`; no alternative build was returned. Its sal-v4 prior-Term reached-band rows and CVSG table support the quoted historical figures. They are not substituted for **the stamped segment base rate**. Baseline, basis, and skill remain the harness's, using the prediction's frozen sal-v4 context rather than this evaluator's later sal-v8 context.

## Predicted reasoning

**Quality: 0.65.** The central grant/plenary call and expected adverse SG assessment held. The SG's staged October 7 brief recommends the reformulated first question, and the order follows that recommendation. However, the primary forecast that both questions would be taken essentially as written failed. Naming a first-question-only fallback earns partial qualitative recognition, not credit for the primary call. The expectation of exactly one additional scheduled distribution was also too narrow: there were two, although the allowance of at most one relist fits. The expected late-November/December brief and January consideration were later than reality. The central outcome and mechanism were substantially right, but scope and chronology prevent a higher grade. Conditional denial writings and the future argument date are not penalized as unobserved events.

## Leakage and record limitations

The log identifies forward mode with 31/31 captured calls. The September 18 prediction predates both the October 7 SG brief and November 13 disposition. Its own-case CourtListener checks are legitimate forward retrieval; neither later-than-baseline information nor the 2025 lower-court ruling is the target disposition. The reasoning and retrieval note report no SG filing or decision. Therefore outcome material retrieved is false, influence is `not_applicable`, and leakage suspected is false.

Call 28 nevertheless reads an unrelated case's prediction and companion files as an output example. A cell-level scope flag preserves that concern; the staged slice does not establish retrieval of this case's outcome or influence on its probability. The historical report of a malformed QP extract is not contradicted by the corrected extract provisioned now. No majority opinion is staged, which is ordinary for this cert event. The independent stakes assessment is 0.62 for nationally important but technically bounded offering-disclosure litigation.
