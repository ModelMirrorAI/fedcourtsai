# Evaluation: gemini-baseline

## Ground truth and scoring scope

This is a cert-stage petition-disposition cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicted `denied`, so exact-label accuracy is 1. This is a correct modal call, not proof that its probability was calibrated or that the Court adopted its explanation. The outcome supplies no reasons for denial.

Votes are not scored at the cert stage. The forecast document was read for context only; neither it nor the quantitative claims contribute to reasoning quality. Claim scores remain the harness's responsibility. No semantic grades are written because this is not a merits cell.

## Baseline

The candidate's own frozen context records Term 2025, band `elevated`, and salience version `sal-v4`, matching the heading in the committed `metrics/statpack.md`. I use the bracketed reached population, so `base_rate_basis = risk_set`, not the terminal band and not the evaluator's decided-docket context.

The rendered table contains 10 of 10 Terms. Eight precede this case's Term: 2024 (17.9%, n=336), 2023 (17.5%, n=354), 2022 (19.0%, n=300), 2021 (20.5%, n=342), 2020 (16.1%, n=397), 2019 (13.8%, n=334), 2018 (15.9%, n=347), and 2017 (17.5%, n=400). Pooling the displayed percentages weighted by their resolved denominators gives n=2,810 and rate 0.172379359430605. Terms 2025 and 2026 are excluded. The rate is approximate because the published percentages are rounded; it is not an exact reconstructed grant count. The denial baseline Brier is 0.029714643557706. There is no rendered-window truncation to flag. These are committed-pack, denial-reweighted live/historical-slice estimates, not a fresh remote-corpus measurement.

With P(grant)=0.40, Brier = (0.40 - 0)^2 = 0.1600. Brier skill = 1 - 0.1600/baseline Brier = -4.384550539510. This is a single-event comparison, not a cohort performance claim.

## Reasoning quality: 0.44

The short rationale identifies relevant positive signals: a requested response after waiver, the asserted territorial-scope split, and foreign-relations stakes. It also starts near the right elevated reached-band rate. These points make a grant probability above the routine low-signal petition rate intelligible.

The analysis does not adequately explain moving from roughly 17% to 40%. It omits the principal counterweights developed in the provisioned opposition: interlocutory posture, pendent appellate jurisdiction, and the argument that the old conflict rarely determines outcomes. Acknowledging that the opposition calls the split stale is not a substantive engagement with those objections. The rationale treats foreign-relations subject matter as supporting a high likelihood of executive-branch consultation, then uses that expected consultation to support eventual review, without evidence for the size of either inference or accounting for consultation that recommends denial. The narrative does not show that a response-request adjustment is incremental to the selected elevated-band baseline.

Its reference to strictly prior 10 Terms is also imprecise: only eight displayed rows precede Term 2025, and it supplies neither weights nor an independently reproducible pool. The approximate 17% level is nevertheless close to the appropriate displayed baseline. The grade reflects incomplete balancing and an unsupported probability adjustment, not brevity alone, and not a separate grade of the CVSG/relist claims or forecast document. The denied label is correct, but the unreasoned denial does not establish that any proposed legal ground was adopted or rejected.

## Leakage assessment

The log is forward, with 25 calls dated September 18 and zero result-capture coverage. I therefore assess query intent and the reasoning, not supposed absence of returned material. The recorded reads concern local instructions, the pre-decision snapshot, questions presented, the statpack, and split-related excerpts from the briefs; the remaining calls write or validate output. No external outcome query or outcome-file read is shown. The rationale forecasts unresolved proceedings and does not presuppose the October 5 denial. The absence of captured results limits retrospective auditing but is the log's standing shape, not itself a defect or evidence of leakage. On the available evidence, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
