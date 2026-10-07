# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage cell. The supplied outcome records denial on October 5,
2026, with `actual_granted = 0`; the provisioned October 5 snapshot agrees.
claude-baseline predicted `denied` with grant probability 0.10 on September 17.
The exact-label score is **1** and the Brier score is **0.0100**.

The candidate's frozen context supplies Term 2025 and band `elevated` under
`sal-v4`. The committed statpack's heading matches. I use the bracketed
`reached` risk-set rates, not terminal rates or the evaluator's context.
The strictly-prior displayed Terms 2024 through 2017 contribute, respectively,
17.9%/336, 17.5%/354, 19.0%/300, 20.5%/342, 16.1%/397, 13.8%/334,
15.9%/347, and 17.5%/400, where each pair is rate/weighted resolutions.
Pooling the displayed rounded rates gives 484.386 / 2,810 =
**0.172379359430605**. Baseline Brier is this rate squared; skill is
`1 - 0.0100 / rate^2` = **0.6634655912806073**.

The table renders 10 of 10 Terms; 2025 and 2026 are excluded. There is no
rendered-window shortfall. This is a denial-reweighted historical/live-slice
estimate, not a current census. No live corpus blob was consulted, and no
corpus freshness is asserted. The small difference from the candidate's
484/2,810 anchor reflects my use of the rounded Markdown rates rather than
an asserted change in the population.

## Reasoning quality: 0.82

The rationale gives a coherent explanation for discounting the elevated-band
anchor: no demonstrated conflicting holding, the elements/means distinction,
Richardson's discussion of continuous child-abuse offenses, and the facial
challenge's vehicle disadvantages. It recognizes the petition's counterargument
that Ramos changes the incorporation premise, and avoids simply equating
the response request with four votes to grant. The provisioned opposition's
Richardson discussion and the lower opinion at appendix 22a–23a support those
descriptions of the parties' positions and posture.

The main weaknesses are the lightly weighted but unverified recollection of
comparable cert denials, speculative chambers motives and presentation-based
discounts, and an incompletely substantiated numerical adjustment from roughly
17% to 10%. The analysis could distinguish more explicitly between a
response-driven redistribution and substantive reconsideration at conference.
These are limitations of the reasoning, not penalties for its probability or
for an unobserved merits outcome. The denial confirms the predicted label;
it supplies no explanation endorsing either side's constitutional analysis.

Only `reasoning.md` is graded for reasoning quality. The forecast document was
read for context, not scored. Mechanical claim scores remain the harness's;
no semantic grades or vote accuracy are written on this cert cell.

## Leakage

The captured log labels the prediction forward and records 33 calls with
capture coverage 1.0. The calls occurred on September 17, before resolution.
Their subjects include prior authorities, a generic corpus query, and the
September 15 reply identified in the baseline. The available log and prose
show no target-case disposition material or already-decided premise. A null
document date alone proves nothing about a result's contents. On the combined
timing and content evidence, outcome material is not shown, influence is
`not_applicable`, and `leakage_suspected` is false.
