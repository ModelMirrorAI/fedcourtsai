# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a **cert-stage** cell. The supplied outcome records `denied`, `actual_granted = 0`, and resolution on October 5, 2026. gemini-baseline's September 16 prediction also names `denied` with P(any grant) = 0.015. Thus **correct = 1** and **Brier = 0.000225**, from `(0.015 - 0)^2`.

The evaluation baseline is computed independently of the candidate's asserted anchor. Its frozen context records `band = baseline`, `salience_version = sal-v4`, and Term **2025**. The matching sal-v4 section of committed `metrics/statpack.md` supplies the bracketed reached rates. For Terms 2017–2024, the rate/weighted-denominator pairs are 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. Pooling all these strictly-prior rows gives **0.05120250431778929** over **11,580** weighted resolved petitions, using the `risk_set` basis. Neither the case's own Term nor the resolution Term enters the pool. The caption displays 10 of 10 Terms, so the rendered window does not hide additional pack Terms.

The denominator and rate are taken from rounded, denial-reweighted committed table entries; this is not a refreshed corpus estimate and no corpus-wide vintage is asserted. The baseline loss is approximately 0.002621696448413231; the single-event skill score is **0.9141777072871346**. gemini-baseline's imperfect explanation of its anchor does not change its submitted probability or the mechanical scores. One successful low-probability forecast cannot establish calibration.

## Reasoning quality: 0.55

The concise rationale identifies relevant vehicle concerns: the opposition disputes a recognized property interest, contests complete loss of access, and advances a limitations defense. These observations support viewing the case as an unattractive vehicle for the federal question. The text attributes the allegations to respondents rather than presenting all contested facts as independently established. Its modal denial agrees with the outcome.

The probability justification nevertheless has substantial defects. It invokes the current-Term 2025 reached rate and an unspecified historical figure instead of explicitly pooling strictly-prior Terms. It then treats a roughly 1.2% terminal zero-relist figure as the rate faced at first distribution, even though future relisting is still possible. The committed zero-relist row also distinguishes 1.2% `granted` from 0.5% `gvr`; the forecast's any-grant axis includes both. Finally, moving from 1.2% to 1.5% is an increase, not the stated slight downward adjustment. A downward adjustment from a larger reached-band anchor could be coherent, but the text does not resolve which anchor actually determines the number.

The legal discussion mostly repeats the opposition's three obstacles without testing them against the petition or the underlying affirmance. Appendix A, pages 7a–10a of the provisioned petition, separates the historic claims' limitations problem from the recent access theory's property-interest problem; pages 10a–11a also identify a preservation issue for the statutory-entitlement argument. The petition's pages 7–9 explain why the asserted taking arose upon loss of replacement access. gemini-baseline does not engage these distinctions or the federal challenge to reliance on state-law property labels. It supplies a plausible vehicle summary, but not a balanced enough analysis to justify a high soundness score.

These deductions concern the reasoning and its numerical logic, not the brevity of the document itself or the correctness of its final label. The denial does not reveal the Court's reasons and cannot validate the opposition's merits position. Only `reasoning.md` is graded; the forecast prose and mechanical claims are not scored here.

## Leakage and scope

The harness log labels the prediction **forward**. The prediction date, September 16, precedes the recorded October 5 denial. All **29** marker-carrying calls are `unobserved`, giving capture coverage **0.0**. This is a telemetry limit, not a failed retrieval or proof that nothing was returned. Assessment therefore rests on the query slices and the prose: reads target the provisioned September 16 snapshot and documents, the committed statpack, contracts and schemas, plus operational output and validation commands. No visible query targets later history or this petition's disposition, and the reasoning contains no already-decided fact.

On that evidence, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is a finding of no identified outcome exposure, not a claim to have inspected unlogged results. The same-Term baseline mistake is a population/time-window methodology defect; it does not establish retrieval of this case's future outcome. The absence of the candidate's unstaged flags is not used as evidence of cleanliness.

No vote accuracy or semantic grades are written on this cert cell. Structured claim scores and provenance stamps remain the harness's. The petition manifest marks the extraction truncated, but the passages discussed here are available. No independent big-case assessment is supplied.
