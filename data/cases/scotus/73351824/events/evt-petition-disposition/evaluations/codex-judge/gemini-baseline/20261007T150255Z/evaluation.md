# Evaluation: gemini-baseline

## Outcome and arithmetic

This is a cert-stage evaluation. The authoritative outcome records denial on October 5, 2026, with actual_granted = 0. The candidate predicted denied with P(grant) = 0.12: correct = 1 and Brier = (0.12 - 0)^2 = 0.0144. The denial does not establish why the Court declined review.

The prediction froze baseline, sal-v4, Term 2025. The committed statpack's sal-v4 heading matches. Pooling baseline's bracketed reached percentages over every rendered prior Term, 2017–2024, gives 592.925 weighted grant equivalents / 11,580 weighted resolutions = 0.05120250431778929. The numerator reflects rounded displayed percentages, not an exact grant count. Basis is risk_set, not terminal; Terms 2025 and 2026 are excluded. The table renders 10 of 10 Terms, so no rendered-window omission applies. Skill is 1 - 0.0144 / 0.05120250431778929^2 = -4.492626733623387. A correct modal call can still lose to the lower-probability baseline on this denial; this is not an aggregate calibration finding. Rates describe the supplied denial-reweighted live/historical slice, not a refreshed census. No corpus freshness lookup was performed.

## Reasoning quality: 0.60

The rationale sensibly distinguishes an important unresolved constitutional issue from a difficult procedural vehicle and leaves denial strongly favored. It identifies the response request, amicus interest, and lack of completed relists as conditioning information rather than treating the petition as already granted.

Its analysis remains thin on the obstacle central to this record: the state court's discretionary intervention ruling and its separate retaliation/causation analysis. Appendix A, pages 31a–35a, supports a more substantial vehicle discount than the brief observation that the posture is messy. Calling the refusal to hear the constitutional challenge a strong vehicle argument adopts the petition's framing without examining the alternative grounds. The counsel signal is also imprecise: the petition identifies Fiddler and Goldwater counsel; PLF's amicus involvement is not the same thing. The approximate baseline is reasonable, but the adjustment to 12% is not quantitatively supported. These are weaknesses in the reasoning, not deductions for missing auxiliary outcome claims.

## Leakage and scope

The log records forward mode and only September 16 activity, before resolution. All 22 results are unobserved, so neither absent document dates nor the candidate's reported failed corpus command independently proves what returned. The visible queries and prose nevertheless show no target-case disposition retrieval or outcome-dependent reasoning. I record retrieved_outcome_material = false and influence = not_applicable, with that capture limitation explicit.

Only reasoning.md receives the qualitative score. The forecast document was read for context; quantitative claims remain for the harness. Cert votes and semantic propositions are not scored. The optional stakes assessment is omitted because no independent assessment was fixed before candidate stakes values became visible in the staged material.
