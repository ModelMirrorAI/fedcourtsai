# Evaluation: codex-baseline

## Disposition and probability

The candidate predicts `denied`, matching the outcome: `correct = 1`. With P(any grant) = 0.18 and actual_granted = 0, the Brier score is `(0.18 - 0)^2 = 0.0324`.

## Reasoning quality: 0.93

The rationale offers a notably balanced cert analysis. It separates the potentially important Dean conflict and mandamus issue from the government's timing, performance, preservation and vehicle objections. It attributes disputed propositions to the parties rather than silently treating advocacy as fact. It also reports checking Dean's historical holding directly, including the potentially distinguishing post-agreement witness-list act. The captured log corroborates a citation lookup, opinion read and focused passage search. The provisioned opposition pp. 15-18 also describes that distinction; the separately retrieved Dean opinion body is not itself staged here.

The analysis appropriately distinguishes rescheduling from completed conference consideration, retains the frozen context, distinguishes stakes from grant probability, and describes its probability adjustments as judgmental rather than empirically fitted. It acknowledges the missing reply and does not invent its contents. Limitations remain: the offsetting legal adjustments are not quantitatively estimated, and the available record cannot establish how strongly the Court would weigh the competing Dean and vehicle arguments. These are modest limits on an otherwise well-supported rationale. The correct denial does not prove the Court accepted the government's reasons, and a higher Brier score than another candidate is not itself a reasoning defect.

## Leakage assessment

The harness log records `forward`, 31 calls, with 29 captured results (93.55%). Two general Court Rule 10/rules-PDF attempts are unobserved; their results cannot be characterized as empty merely because the candidate reports no usable content. Their queries are general procedural research, not a search for this case's result. Other substantive external calls concern the 2009 Dean precedent, not this petition's subsequent history. Collapsed `other` tool names are not suspicious by themselves.

No logged query or rationale shows the target's October 19 disposition or an already-decided petition. The October 5-6 prediction activity preceded resolution. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, while preserving the visibility limit on the two unobserved results.

## Scoring scope and baseline

This is a cert-stage evaluation. The realized outcome is `denied` on October 19, 2026, with `actual_granted = 0`; denial does not establish the Court's reasons or endorse the lower court's reasoning. The candidate's frozen context is forward, Term 2025, band `elevated`, salience version `sal-v4`, snapshot October 5, 2026, with two distributions and no cutoff. The evaluator's later terminal `high` band is not the candidate's information set and is not substituted for it.

The prediction froze a band, so the segment base rate, its basis and skill are left to the harness. Any baseline comparison uses the stamped segment base rate; I neither pool nor quote an alternative. Cert votes are unscored, and no vote accuracy is written. This stage declares no semantic set. Mechanical claim scores, process version and other harness stamps are left absent.

Only `reasoning.md` informs reasoning quality. I read `predicted_reasoning.md` for context but do not grade that document or the auxiliary quantitative claims. I checked the provisioned question presented, petition pp. 17-19, and opposition pp. 8-10 and 13-19 for the competing performance, Dean and mandamus arguments. These supplied briefs support the rationale's account of the parties' positions; the denial does not decide which position is right. Later-added provisioned filings are not assumed to have been available to the predictor.

## Stakes

My case-level significance assessment is 0.88 for each candidate: exceptional human and institutional stakes surrounding death exposure and government plea commitments in the September 11 prosecutions, tempered by a narrow performance-rule and mandamus issue. This is an independent stakes read, not a predictor-agreement score.
