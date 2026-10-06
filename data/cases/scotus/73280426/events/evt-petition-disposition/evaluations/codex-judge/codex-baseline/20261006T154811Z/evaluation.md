# Evaluation of codex-baseline

## Outcome and scores

This is a cert-stage evaluation of the September 16, 2026 prediction. The authoritative outcome is `gvr`, with `actual_granted = 1`, resolved October 5, 2026. The final entry in the provisioned October 5 snapshot specifies reconsideration in light of Louisiana v. Callais. The candidate's `denied` label does not match, so correctness is **0**. Brier = (0.30 - 1)^2 = **0.49**. Recognition of a possible GVR in the rationale does not change the exact-label score.

## Baseline

The prediction's frozen context supplies Term 2025, `elevated`, and `sal-v4`, matching the heading in the committed statpack. Accordingly the basis is `risk_set`, using the bracketed `reached` figures for every displayed Term before 2025, not terminal-band rates or the evaluator's context. For 2017–2024, the displayed rate/weighted-resolved pairs are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336.

The rounded-table reconstruction is 484.386 / 2,810 = **0.172379359430605**, not an integer grant count. Baseline Brier = 0.6849559246964957; skill = 1 - 0.49 / 0.6849559246964957 = **0.2846255031415062**. Thus the forecast beats this low baseline on this realized grant while missing the modal label. This is a single-cell comparison, not a general performance claim. The candidate reported a slightly different, more precise companion-JSON pool; this evaluation consistently uses the rendered markdown figures required by the task. The caption renders all 10 of 10 Terms, so there is no window-divergence flag. The pack is a committed denial-reweighted live/historical estimate, not a newly queried corpus vintage.

## Reasoning quality: 0.84

The rationale is careful and case-specific despite its incorrect headline. It distinguishes standing to appeal the liability decision from the challenge to the remedy, treats disputed injury and racial-predominance assertions as advocacy rather than established facts, addresses preservation, and identifies a credible intervening-precedent GVR route. It also avoids mistaking a government respondent for a government petitioner, double-counting the band and terminal relist statistics, or treating the earlier expedition denial as a cert denial.

The main analytical limitation is an incomplete account of the remand evidence. The candidate expressly lacked the separate State response and petitioners' reply and therefore could not assess their positions. Its denial-centered balance emphasizes objections to plenary review more strongly than the cheaper reconsideration route it itself recognizes. The resulting GVR illustrates that those objections did not prevent summary remand; it does not establish that the objections were legally unsound or resolve the underlying merits. A high reasoning score remains warranted for the transparent treatment of uncertainty and the specific competing explanations, rather than for predicting the actual label.

The number grades the substantive soundness of `reasoning.md` alone. Neither the forecast document nor the structured quantitative claims are independently scored here, and no hindsight penalty is imposed simply for allocating less than 50% to an outcome that occurred.

## Leakage and scope

The log records forward mode, 30 calls, and 28 captured results. The two unobserved web rows concern Callais and a rules PDF. Their missing result bodies cannot be credited as evidence that the searches returned nothing, even though the candidate reports no usable content. The recorded queries are not searches for this petition's disposition, and all calls precede its October 5 resolution. Discussion of an already-decided precedent in a June brief is legitimate forward context. No reasoning indicates knowledge of this petition's eventual GVR. Leakage influence is `not_applicable`, with `leakage_suspected = false`.

Cert vote accuracy and semantic grades are omitted. The harness owns claim scores and provenance stamps. No independent big-case grade is supplied.
