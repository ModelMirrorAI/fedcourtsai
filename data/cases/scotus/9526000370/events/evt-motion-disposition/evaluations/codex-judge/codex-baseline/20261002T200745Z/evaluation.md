# Evaluation: codex-baseline

## Outcome and quantitative score

The supplied event is an interim stay application, resolved `denied` on October 1, 2026, with `actual_granted = 0`; the evaluator snapshot records denial by Justice Kagan. codex-baseline selected `granted` at probability 0.62. Exact-label correctness is **0** and Brier loss is **(0.62 - 0)^2 = 0.3844**. The unexplained denial establishes no specific legal rationale.

## Reasoning quality: 0.82

This is a careful, substantially balanced analysis despite the incorrect label. It separates the requested interim relief from underlying liability, identifies the arrival-position baseline, and avoids interpreting absent arrival-stage signals as final facts. It documents the historical anchor's population and coverage limits, explicitly distinguishes artifact vintage from corpus freshness, and does not present aggregate escalation totals as measured conditional probabilities.

The rationale engages the adverse material in the application's appendix rather than accepting the applicant's framing alone. It distinguishes Judge Forrest's preference for an administrative stay and expedited merits-panel consideration from support for a full stay pending appeal, a distinction confirmed by App. 1–2. It weighs the transfer of state authority against the reported continuing patient harms and unsuccessful prior remedies, and acknowledges that the truncated appendix and missing respondent filing limit the adversarial record. Its general-authority retrieval is identified separately from case facts.

The remaining weakness is the size of the move from a roughly 10.5% historical anchor to 62%. Institutional stakes and the approaching transfer supply a plausible direction of adjustment, but not an empirical or tightly reasoned magnitude. The candidate explains substantial contrary evidence without fully explaining why the State's showing should nevertheless cross the more-likely-than-not threshold. It correctly labels the result judgmental rather than fitted. That limitation is apparent ex ante; the wrong label does not itself lower the reasoning grade.

The forecast document and increment claims are context only. Their observed success or failure contributes neither to this reasoning grade nor to an agent-written claim score. The unexplained disposition does not prove that the Court adopted the candidate's stated downside scenario.

## Baseline and scope

This is an **interim** cell, so baseline and skill belong to the harness. `segment_base_rate` and `brier_skill_score` are omitted, with `base_rate_basis` null. The inspected committed statpack's eligible substantive rows show 17 grants/226 resolutions in application-Term 2025 and 14/70 in 2024; the displayed earlier 2016–2023 rows add none. The pool clears the 50-resolution floor, with no missing-section or thin-pool refusal apparent from this artifact. No live corpus freshness is asserted. Coverage is uneven; the resolved population is selected by parseable disposition text, counts withdrawals/dismissals as ungranted and mixed relief as denial-first, and is broader than the escalation-selected predicted population.

No interim vote accuracy, semantic grades, or mechanical claim scores are written. The optional independent stakes assessment is omitted.

## Leakage

The prediction's log and frozen context say `forward`. Its September 27 execution predates the October 1 resolution; the arrival-position anchor and September 17 cutoff constrain the baseline rather than forward retrieval. Queries concern the provisioned record, statpack, and general authorities. No visible query seeks this application's later history or disposition, and the reasoning does not presuppose the outcome.

Twenty-four of 26 result markers are captured. The two unobserved web rows concern general legal authorities; their null dates and the candidate's statement that no usable content returned do not independently establish empty results. Their query scope supplies no evidence of this application's outcome. A logged instruction-file search expressly excludes the prohibited topic-artifact path, rather than reading it. Outcome material is not shown, influence is `not_applicable`, and leakage is not suspected.
