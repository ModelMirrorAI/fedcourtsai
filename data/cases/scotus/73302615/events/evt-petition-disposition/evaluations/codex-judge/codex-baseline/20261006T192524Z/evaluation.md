# Evaluation: codex-baseline

## Ground truth and scoring scope

This is a cert-stage petition-disposition cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicted `denied`, so exact-label accuracy is 1. This is a correct modal call, not proof that its probability was calibrated or that the Court adopted its explanation. The outcome supplies no reasons for denial.

Votes are not scored at the cert stage. The forecast document was read for context only; neither it nor the quantitative claims contribute to reasoning quality. Claim scores remain the harness's responsibility. No semantic grades are written because this is not a merits cell.

## Baseline

The candidate's own frozen context records Term 2025, band `elevated`, and salience version `sal-v4`, matching the heading in the committed `metrics/statpack.md`. I use the bracketed reached population, so `base_rate_basis = risk_set`, not the terminal band and not the evaluator's decided-docket context.

The rendered table contains 10 of 10 Terms. Eight precede this case's Term: 2024 (17.9%, n=336), 2023 (17.5%, n=354), 2022 (19.0%, n=300), 2021 (20.5%, n=342), 2020 (16.1%, n=397), 2019 (13.8%, n=334), 2018 (15.9%, n=347), and 2017 (17.5%, n=400). Pooling the displayed percentages weighted by their resolved denominators gives n=2,810 and rate 0.172379359430605. Terms 2025 and 2026 are excluded. The rate is approximate because the published percentages are rounded; it is not an exact reconstructed grant count. The denial baseline Brier is 0.029714643557706. There is no rendered-window truncation to flag. These are committed-pack, denial-reweighted live/historical-slice estimates, not a fresh remote-corpus measurement.

With P(grant)=0.14, Brier = (0.14 - 0)^2 = 0.0196. Brier skill = 1 - 0.0196/baseline Brier = 0.340392558910. This is a single-event comparison, not a cohort performance claim.

## Reasoning quality: 0.90

The rationale is well balanced and grounded in the pre-decision record. It identifies the territorial-scope disagreement while distinguishing the opposition's stale-conflict and limited-recurrence arguments from established findings. It treats interlocutory posture and pendent appellate jurisdiction as vehicle risks rather than declaring an unproved jurisdictional defect. The provisioned opposition's printed pages 25–27 expressly raise those obstacles. It also correctly separates counsel withdrawal from withdrawal of the petition and avoids assuming that two distributions mean two fully briefed conferences.

The prior-Term, frozen-band anchor is appropriate, and the downward adjustment to 14% is explained through competing considerations rather than hindsight. Its cited 484/2,810 anchor comes from its reported unrounded JSON lookup; my slightly different baseline uses the rounded Markdown table as specified here. Neither difference is material to the qualitative grade. The rationale candidly labels its adjustment judgmental, discloses the snapshot's age and additional inputs, and avoids overstating the implications of Simon. The main limitation is that the magnitude of the vehicle and representation discounts is not empirically established. The correct denial does not verify which concern, if any, actually motivated the Court.

## Leakage assessment

The harness log is forward and places retrieval on September 18, before the October 5 resolution. Its dated-letter URL identifies August 26, and the authority searches concern earlier Simon decisions, not the target disposition. Two web results are unobserved, so the candidate's report that those attempts returned nothing cannot be independently confirmed from their capture markers. Their queries nevertheless target a statute and the fixed pre-decision letter, not an outcome. Captured rows have digests rather than full result bodies; null document dates are not affirmative proof of an empty result. The instruction-file search explicitly excludes the labeling-artifact path, rather than opening it. The reasoning neither cites nor presupposes the target denial. Thus `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`; no mis-provisioned-forward evidence appears.
