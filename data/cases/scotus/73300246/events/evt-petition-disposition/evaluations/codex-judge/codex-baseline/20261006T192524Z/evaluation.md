# Evaluation: codex-baseline

## Outcome and quantitative scores

This is a **cert-stage** petition-disposition event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`, no noted dissent from denial, and no votes. codex-baseline's September 16 prediction named `denied` and assigned P(any grant) = 0.025. The exact-label score is **1** and Brier loss is **0.000625**, calculated as `(0.025 - 0)^2`.

The baseline uses the prediction's frozen `baseline` band, `sal-v4` version, and Term **2025**. The matching table in committed `metrics/statpack.md` supplies bracketed reached-baseline rate/weighted-denominator pairs of 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271 for Terms 2017–2024. Their weighted pool is **0.05120250431778929** over **11,580** weighted resolved petitions. This reproduces the candidate's approximate 5.12% prior-Term anchor. Terms 2025 and 2026 are excluded; the October 2026 resolution does not change the case's frozen Term. The table renders 10 of 10 Terms, so no omitted pack window requires a flag.

The basis is `risk_set`, not terminal. Rounded, denial-reweighted rates in the committed artifact make the resulting pool approximate; no new corpus estimate or corpus-wide freshness claim is made. Baseline loss is approximately 0.002621696448413231, and `1 - 0.000625 / baseline_loss` yields **0.7616047424642627**. This realized-event score is not a general calibration finding.

## Reasoning quality: 0.94

The rationale gives a careful explanation of both the anchor and the case-specific adjustment. It distinguishes first distribution from eventual zero-relist status, avoids treating the summer interval as a hold, and identifies the limitations of terminal descriptive cuts. The subjective reduction from roughly 5.12% to 2.5% is expressly labeled judgment rather than a fitted model.

The strongest feature is direct engagement with competing accounts and the underlying state opinion. The provisioned petition's Appendix A, pages 7a–10a, supports the rationale's separation of historical quiet-title/excess-condemnation limitations issues from the access claim's lack of a pleaded property interest. The footnote spanning pages 10a–11a supports the identified waiver of the NRS 408.533 argument. Rather than simply importing the opposition's claim that the entire controversy is time-barred, the candidate explains why the recent-sale theory warrants distinct treatment.

The candidate also recognizes the petitioner's federal-property theory and its account of longstanding permitted access, while explaining why those assertions do not establish the required property interest or total loss of feasible access on this record. The petition's pages 7–9 and the opposition's competing access account support treating those premises as contested, not deciding them from advocacy. The discussion of the alleged conflict appropriately stops short of claiming an independently verified split. The disclosure of missing reply text, petition truncation, and unverified maps/title details makes the evidentiary boundary clear.

The remaining limits are that the precise probability adjustment is not empirically estimated, the asserted conflict is not fully verified, and the factual predicates cannot be resolved from the supplied extracts. These are acknowledged uncertainties rather than concealed assumptions. The outcome is consistent with denial but supplies no substantive rationale; the high quality grade therefore rests on the soundness and care of the pre-decision analysis, not an inference that the Court adopted it. Its larger realized Brier loss does not negate that distinction.

Only `reasoning.md` contributes to this score. The pointed-to forecast document was read for context, but no forecast prose or structured mechanical claim is graded here.

## Leakage and scope

The harness log marks the prediction **forward**. Its September 16 timestamp precedes the October 5 disposition. Of **27** calls, **25** have captured results and **two** are unobserved, matching coverage **0.9259259259259259**. The two unobserved web targets concern the 2023 Tyler precedent and its official opinion URL, not Harvey's subsequent history. The candidate's self-report of no visible web results is not substituted for captured evidence: unobserved means the results are unknown. Captured MCP query slices seek the same general precedent and its discussion of traditional property interests; other logged work concerns provisioned documents, statpack, schemas, arithmetic, and output operations.

Nothing in the visible query targets or reasoning identifies this petition as already decided or relies on its eventual denial. The assessment is `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. Null document dates do not independently prove absence, and the current evaluator's uncut record is not used to reconstruct the candidate's provisioned baseline. The candidate's acknowledgement that a September-named snapshot may contain older source material is an appropriate limit on freshness, not outcome leakage.

Votes remain unscored on this cert event and no semantic grades are declared. Mechanical claim scores and provenance stamps are left absent for the harness. The staged opinion slot is absent and is immaterial to this cert evaluation; the state affirmance used as context is part of the provisioned petition appendix, not a Supreme Court merits opinion. No independent big-case assessment is supplied.
