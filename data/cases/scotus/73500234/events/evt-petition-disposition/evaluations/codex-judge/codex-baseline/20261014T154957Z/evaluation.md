# Evaluation: codex-baseline

## Outcome and numerical score

This cert-stage event resolved as `denied` on October 13, 2026, with `actual_granted = 0`. The prediction's denial label matches exactly: `correct = 1`. The grant probability 0.06 yields Brier score `(0.06 - 0)^2 = 0.0036`. This single observation is not a calibration test.

The prediction froze `baseline`, `sal-v4`, Term 2025. Segment base rate, skill, and basis remain unset pending the harness's calculation. The stamped segment base rate is the only evaluation anchor; I neither reproduce nor independently quote the candidate's pooled rate as one. Cert votes are not scored, no semantic block is declared, and the harness retains quantitative claim scoring.

## Reasoning quality: 0.92

The rationale closely connects the probability to the supplied dispute without treating advocacy as adjudicated fact. It recognizes that the changed jurisdictional/summary-judgment standards give the remand argument substance, then confronts the independent de novo affirmance and the earlier Court's reservation of remand consequences. It explains why the asserted accrual conflict may not involve equivalent easements or procedural postures and why the alternative private-easement-holder explanation raises a preservation issue. The supplied opposition, pages 5–6 and 10–14, supports these descriptions of the government's position.

The candidate distinguishes a private petitioner from a federal petitioner, a reached-band anchor from terminal-state cuts, scheduling events from affirmative Court interest, and an absence of later attention from proof that none could occur. It identifies the missing reply, appendix, and underlying evidentiary record in its own information set and leaves contested descriptions conditional. These are substantive strengths in the rationale rather than rewards for length or a correct label.

The remaining uncertainty is quantitative: the small adjustment for a return trip and institutional concerns is an expert judgment, not an empirically estimated effect, and the contested alternative-ground analysis was not checked against the actual appellate record. The candidate candidly acknowledges those limits. I have not independently verified its historical base-rate arithmetic. The high score reflects its explicit handling of evidentiary and inferential uncertainty, not presumed confirmation of its legal theory by a bare denial.

Only `reasoning.md`'s analytical quality is graded here. Forecast details and separate claim probabilities do not contribute to this score; neither does the candidate's own stakes number. The outcome establishes no merits holding or explanation of the denial.

## Leakage assessment

The log records `forward`, with activity October 3 before the October 13 resolution. It contains 36 calls, 32 captured and four unobserved web attempts, for capture coverage 0.8888888888888888. The four web queries are general Rule 10/rules-guidance requests, not searches for this petition. I do not infer empty results from their null dates or from the candidate's self-report; the results were not captured. Their visible subjects and the rationale nevertheless provide no evidence of present-case outcome exposure. The earlier 2023 decision is ordinary procedural history. There is no indication that the resolved petition was mis-provisioned forward. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

## Independent stakes assessment

My case-level score is 0.25: potentially recurring remand and Quiet Title Act notice questions, but limited demonstrated reach beyond a fact-sensitive road-easement dispute with an alternative ground for affirmance. It is not derived from the candidate's stakes estimate.
