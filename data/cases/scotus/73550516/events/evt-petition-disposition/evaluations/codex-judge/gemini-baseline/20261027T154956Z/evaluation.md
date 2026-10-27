# Evaluation: gemini-baseline

## Outcome and quantitative assessment

This is a cert-stage event. The recorded outcome is **dismissed**, resolved October 20, 2026, with `actual_granted = 0`. The October 26 snapshot specifies a joint stipulation filed October 19 and a Rule 46 dismissal October 20. There was no cert denial or substantive resolution of the arbitration question.

The candidate predicted **denied**, yielding exact-label `correct = 0`. Its 0.18 grant-family probability yields `(0.18 - 0)^2 = 0.0324`. Correctly favoring the non-grant binary does not earn a correct disposition label. No cert votes are scored.

The prediction froze `baseline`, `sal-v4`, Term 2025. The **stamped segment base rate** and Brier skill are the harness's; no independent baseline, basis assignment, or skill estimate is supplied. Mechanical claims and the forecast document are not graded, and no semantic set applies.

## Reasoning quality: 0.50

The short rationale identifies the relevant source-of-law question and the petition's requested hold, and it correctly recognizes that a follower GVR belongs on the grant binary. Its lead-grant-times-reversal structure is a useful starting point for explaining 0.18.

However, it calls the alleged conflict a clean 4-1 split without explaining the authorities, competing contract constructions, preservation, or vehicle limitations. The lead's grant estimate and reversal assumption are thinly supported, and the supplied petition does not establish the lead docket number the rationale gives. Most importantly, the rationale treats a response request as guaranteeing redistribution without considering withdrawal or dismissal. The snapshot's subsequent stipulated dismissal shows why that unconditional procedural premise was too strong; it does not disprove the alleged doctrinal conflict. The grade reflects these analytical gaps in `reasoning.md`, not the realized value of any mechanical claim or the separate forecast document. Brevity itself is not penalized.

## Leakage

The log is **forward**, with 29 calls and result-capture coverage 0.0: every result is unobserved. This is a visibility limitation, not evidence of failed searches or misconduct. I assess the visible queries and prose rather than treating null document dates as clean results. Queries include this case's caption qualified by Fifth Circuit, companion names, and a corpus query with a pre-October-6 bound. No visible text discloses this petition's dismissal, and the October 6 prediction predates both its October 19 stipulation and October 20 resolution. The decided-case-forward exception is unsupported. `retrieved_outcome_material = false` records no affirmative evidence of such material, not a claim that every result was inspected; influence is `not_applicable` and `leakage_suspected = false`.

Only provisioned evidence was used for this evaluation; no external case facts were retrieved.
