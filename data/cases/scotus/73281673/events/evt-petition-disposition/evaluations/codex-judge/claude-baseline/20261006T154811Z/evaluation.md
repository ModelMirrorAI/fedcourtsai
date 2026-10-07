# Evaluation: claude-baseline

## Outcome and numerical score

This cert-stage, distribution-moment evaluation scores the blinded prediction from run `20260916T170237Z`. The provisioned outcome records denial on October 5, 2026, with `actual_granted = 0`. claude-baseline named `denied`, with P(any grant) = 0.08. Its exact-label correctness is **1**, and **Brier loss = (0.08 - 0)^2 = 0.0064**.

The prediction's own frozen context supplies band `elevated`, version `sal-v4`, and docket Term 2025. The committed `metrics/statpack.md` band-table heading matches that version and renders 10 of 10 Terms. The baseline pools the bracketed **reached** rates for every displayed strictly-prior Term: 2024: 17.9%/336; 2023: 17.5%/354; 2022: 19.0%/300; 2021: 20.5%/342; 2020: 16.1%/397; 2019: 13.8%/334; 2018: 15.9%/347; 2017: 17.5%/400. The weighted sum is 484.386 and denominator 2,810, giving **0.17237935943060498**, with basis `risk_set`. These are denial-reweighted committed-pack estimates reconstructed from rounded percentages, not exact grant counts or a fresh corpus measurement. Neither the evaluator's terminal band nor the October Term of the denial is substituted. There is no rendered-window divergence.

With baseline loss approximately 0.02971464356, **Brier skill = 1 - 0.0064 / baseline_loss = 0.7846179784195887**. This is descriptive of one outcome, not an aggregate performance claim.

## Reasoning quality: 0.84

The rationale identifies the decisive forecasting tension: a conceded, developing private-search conflict versus serious problems with this particular interlocutory state-court vehicle. It gives appropriate prominence to the BIO's finality argument and remaining proceedings, considers alternative routes to admitting the phone evidence, and distinguishes issue significance from certworthiness. It correctly declines to treat two distributions separated by a response request as substantive repeated relists, and it uses the frozen risk-set baseline rather than the terminal relist rate.

The additional Braun retrieval is relevant forward context. The rationale distinguishes that panel's probable-cause disposition from the concurrence's view of the underlying private-search conflict, and explains why an expanding split could increase interest without curing this petition's remedial obstacles. The transcript corroborates searches and opinion reads; its digests are not a substitute for the external opinions' full text, which I have not independently retrieved. The grade does not rest on independently certifying every characterization of those authorities.

Two weaknesses lower the score. First, the claim that the petition does not answer the alternative-evidence problem is too categorical: the provisioned petition at printed pages 25–26 expressly contests whether a CyberTip alone establishes probable cause, and pages 28–30 attack good faith. Those arguments may fail, but they should be evaluated rather than described as absent. Second, the negative inference from counsel's apparent lack of Supreme Court experience and the generalization that the Court waits for experienced counsel are less well supported than the identified jurisdictional and record defects. The numerical adjustment to 8% also remains a judgment rather than an empirically fitted rate.

The denial is consistent with the forecast but does not reveal which consideration motivated the Court. Only the analysis in `reasoning.md` contributes to this grade. The forecast document and the structured quantitative claims are not scored here. Vote accuracy is omitted on this cert cell; no semantic grading applies. No independent big-case assessment is supplied.

## Leakage assessment

The harness identifies a forward prediction and records September 16 activity before the October 5 denial. All 41 calls carry captured results. The case-specific search result is dated January 14, 2026, corresponding to the lower-court decision; Braun metadata is dated August 20, 2026. These are not the cert disposition being predicted. Topical searches for companions and the broad granted-case corpus lookup are legitimate forward context. The rationale explicitly frames the September 28 conference as upcoming, and neither it nor the log shows the petition already resolved.

There is no evidence of this petition's outcome being retrieved: `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`. The evaluator's October 5 snapshot is used only as provisioned evaluation evidence, not to reconstruct the predictor's September input exposure. No adverse inference is drawn from the absence of the predictor's unstaged flags.
