# Evaluation: codex-baseline

## Outcome and quantitative scores

This cert-stage event resolved as `denied` on October 5, 2026, with `actual_granted = 0`. The predicted label matches, giving correctness **1**. P(grant) = 0.02 produces Brier **0.0004**.

The candidate's own frozen context supplies Term 2025, `baseline`, and `sal-v4`, matching the committed table. I pool the bracketed reached population over every displayed strictly-prior row, OT2017–OT2024, using the corresponding unrounded `metrics/statpack.json` values. The weighted denominator is 11,580 and numerator 593: baseline **0.05120898100172712**, with basis `risk_set`. The executed `prediction_base_rate` calculation agrees. Brier skill is 1 - 0.0004 / baseline² = **0.8474656262352516**. Neither the evaluator's terminal context nor OT2025–OT2026 enters the baseline. These are committed-pack estimates; I did not query current corpus state or establish a new corpus vintage.

## Reasoning quality: 0.92

The analysis is unusually well grounded in the supplied record. It distinguishes the private petitioner from the state respondent when selecting a baseline, uses the frozen risk set rather than terminal outcomes, and avoids treating a missing opposition as a waiver. Its account of the unpublished appellate decision tracks Appendix A: the panel assumed implied bias could be clearly established, yet upheld the state decision on reasonableness and the thin juror-specific facts. That preserves the distinction between identifying a constitutional concern and establishing a suitable habeas vehicle.

The rationale also tests the asserted conflict rather than accepting the petition's characterization. Its discussion distinguishes voluntary disclosure from concealment or more developed evidence of emotional involvement. The petition and appended opinion support those distinctions. The historical-precedent retrieval is relevant to that inquiry, although I did not independently repeat the external lookups. The discussion of countervailing personal stakes and recurring jury concerns keeps the downward adjustment from becoming a categorical impossibility claim.

The remaining limitation is calibration: the movement from approximately 5.1% to 2% is judgmental, not empirically fitted to this combination of obstacles. The candidate acknowledges that limitation, separates terminal descriptive statistics from forward transition probabilities, and identifies source-date uncertainty without building a timing argument upon it. The denial is consistent with the prediction, but supplies no Court explanation confirming the proposed reasons. The grade rewards analytical discipline, not hindsight correctness or retrieval volume.

## Leakage and scope

The recorded mode is forward. The September 17 forecast and retrieval predate the October 5 denial. Of 39 logged calls, 37 have captured results; two historical-authority web calls are unobserved. Their queries, rather than missing dates, are the relevant evidence: neither targets this petition's disposition. The self-report of unusable web content is not independent proof of empty results. The remaining record shows no case-outcome material or mis-provisioned decided case. Outcome retrieval is assessed false, influence `not_applicable`, and suspected leakage false.

The grade uses `reasoning.md` only. The forecast prose is contextual and unscored; quantitative claims are left to the harness. Cert votes and semantic propositions are not scored, and no independent big-case assessment is supplied.
