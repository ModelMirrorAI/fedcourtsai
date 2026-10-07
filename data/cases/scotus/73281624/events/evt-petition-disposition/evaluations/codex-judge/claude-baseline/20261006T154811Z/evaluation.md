# Evaluation: claude-baseline

## Outcome and quantitative score

The cert-stage outcome records denied on October 5, 2026, actual_granted = 0. claude-baseline predicted denied on September 17 with P(any grant) = 0.06. Correctness is 1 and Brier loss is 0.06^2 = 0.0036. The denial provides no judicial explanation for choosing among the rationale's proposed reasons.

The candidate's frozen context is elevated, sal-v4, Term 2025, matching the committed statpack heading. The risk_set baseline uses the bracketed reached rates for every rendered prior Term, not terminal-band rates: 2024 (17.9%, n=336), 2023 (17.5%, n=354), 2022 (19.0%, n=300), 2021 (20.5%, n=342), 2020 (16.1%, n=397), 2019 (13.8%, n=334), 2018 (15.9%, n=347), and 2017 (17.5%, n=400). The resolved-weighted rate is 484.386 / 2810 = 0.172379359430605. Published percentages are rounded, so the weighted numerator is an approximation rather than an integer grant count. The candidate's approximate 17% anchor is consistent in scale; the evaluation uses the committed table supplied to this run.

The table renders 10 of 10 Terms, with 2025 and 2026 excluded as non-prior. No version mismatch or rendered-window divergence arises. Skill is 1 - 0.0036 / 0.172379359430605^2 = 0.8788476128610186. This single-event comparison against a denial-reweighted paid risk set is not a calibration result or an aggregate performance claim. No live corpus state or vintage is asserted.

## Reasoning quality: 0.84

The rationale offers a substantive, case-specific justification for moving below the elevated-band anchor. It distinguishes redistribution after a response request from a true relist, recognizes the response request as positive evidence, and weighs it against the absence of a demonstrated conflict, the statutory exclusivity language, and the opposition's preservation objection. It also explains why the market-participant question could nevertheless attract interest. These considerations make the denial call more than a repetition of the low overall grant rate.

Several qualifications keep the score below the top of the scale. The claim that only two Parker merits cases exist since 2010 is stronger than a narrow keyword search can establish. Assertions about counsel experience and the expected presence of amici are weakly supported marginal signals. The Fourth Circuit's unconditional grant rate does not establish an incremental effect after selecting the elevated band, and terminal grant/GVR proportions do not directly identify the reached-band plenary component. The response request explains this docket's trajectory but is not itself the frozen band's numeric criterion: the record carries two distributions. Finally, the claimed failure to preserve heightened rigor comes from the opposition and should be explicitly treated as that party's account, rather than as independently settled fact. These are limitations in evidentiary discipline, not reasons to reverse the otherwise coherent analysis.

The score concerns reasoning.md only. No credit or penalty is assigned for individual forecasts in predicted_reasoning.md or for the structured mechanical claims, which the harness scores separately. The cert-stage vote block and semantic family are unscored. No big-case assessment is supplied.

## Leakage assessment

The log records forward mode and capture coverage 1.0 across 30 calls. The visible retrieval includes supplied materials, a broad corpus query for recent grants, a search for the Fourth Circuit opinion, and a general state-action precedent search. The two dated search results are December 23, 2025, and April 22, 2021, both before this petition's resolution. Neither a broad prior-case query nor a lower-court decision is this petition's Supreme Court outcome.

The September 17 reasoning treats the September 28 conference as future and denies knowledge of an outcome. The log supplies no contrary evidence of this petition already being decided; result digests are not full response text, so the assessment does not claim a verbatim reconstruction of every result. No outcome retrieval is evidenced: retrieved_outcome_material = false, influenced_prediction = not_applicable, leakage_suspected = false. The evaluator's later snapshot is not substituted for the candidate's September 17 baseline.
