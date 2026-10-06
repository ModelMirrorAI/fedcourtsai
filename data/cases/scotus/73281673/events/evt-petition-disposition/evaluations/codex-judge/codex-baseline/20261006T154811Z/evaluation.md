# Evaluation: codex-baseline

## Outcome and numerical score

This is a cert-stage, distribution-moment evaluation of the blinded prediction from run `20260916T170237Z`. The provisioned `outcome.json` records denial on October 5, 2026, with `actual_granted = 0`. codex-baseline predicted `denied`, with P(any grant) = 0.05: exact-label correctness is **1**, and Brier loss is **(0.05 - 0)^2 = 0.0025**.

The baseline uses the prediction's frozen `elevated` band, `sal-v4`, and docket Term 2025, not the evaluator's terminal context or the Term of disposition. The committed `metrics/statpack.md` heading matches that version. Its caption renders 10 of 10 Terms; all eight displayed Terms strictly before 2025 enter the pool. The elevated **reached** rate/weighted-denominator pairs are 2024: 17.9%/336; 2023: 17.5%/354; 2022: 19.0%/300; 2021: 20.5%/342; 2020: 16.1%/397; 2019: 13.8%/334; 2018: 15.9%/347; 2017: 17.5%/400. Their weighted sum is 484.386 over 2,810, giving **0.17237935943060498**, with `base_rate_basis = risk_set`. These are denial-reweighted committed-pack estimates calculated from rounded displayed percentages, not exact grant counts or a newly refreshed corpus measurement. There is no rendered-window divergence.

The baseline loss is approximately 0.02971464356; **1 - 0.0025 / baseline_loss = 0.9158663978201518**. This is a single-event comparison, not evidence of aggregate calibration or general predictive skill.

## Reasoning quality: 0.91

The rationale distinguishes the importance of the private-search conflict from whether this petition is a suitable vehicle. It acknowledges the conflict conceded in the brief in opposition and the response request and amicus support, but gives substantial weight to the State's finality argument, pending proceedings, alternative routes to admitting the evidence, and unresolved privacy questions. The provisioned BIO's jurisdiction section, printed pages 9–15, supports treating finality as a major obstacle; the candidate properly treats the State's position as an argument rather than a Supreme Court ruling.

Its handling of counterarguments is particularly careful. It recognizes that the petition actually challenges good faith and the sufficiency of a CyberTip for probable cause, rather than incorrectly saying that the petition is silent. The petition's printed pages 25–26 and 28–30 support that distinction. It also separates the response-cycle redistribution from repeated substantive conference consideration and avoids substituting a terminal relist bucket for the frozen risk-set baseline.

The rationale discloses the truncated appendix, reliance on the BIO for omitted passages, and unsuccessful attempts to verify an authority. The adjustment from approximately 17.2% to 5% remains a subjective synthesis rather than an estimated conditional rate; the unverified authority and incomplete appendix limit the evidentiary depth. Those limits explain why the score is below perfect. The denial confirms the outcome label, not that the Court adopted any particular jurisdictional or substantive rationale.

Only the soundness of `reasoning.md` is graded here. The forecast document was read for context, but neither its predictions nor the structured claims are scored in this assessment. Vote accuracy is omitted because this is a cert event; no semantic set is graded. No independent big-case assessment is supplied.

## Leakage assessment

The harness log identifies a forward run. Its September 16 calls and the prediction precede the October 5 resolution; the candidate cites a September 15 baseline. The local reads and external query subjects reveal no already-decided disposition of this petition. The current evaluator snapshot is dated October 5 and is not treated as evidence of what the predictor saw.

Result capture covers 28 of 31 calls. The three unobserved web rows concern the older Florida v. Thomas authority and an official report URL. Although the candidate describes receiving no usable content, the log cannot independently establish an empty result for those rows; the assessment rests on their non-case-outcome query scope and the rationale, not on that claimed absence. A query excludes the prohibited labeling directory while locating instruction files; it does not read labeling contents. There is no affirmative evidence of outcome material: `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`.
