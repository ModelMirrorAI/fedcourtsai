# Evaluation: gemini-baseline

## Outcome and numerical scores

This is a cert-stage evaluation. The provisioned outcome records denial on October 5, 2026, with `actual_granted = 0`. gemini-baseline predicted `denied` and P(grant) = 0.25: exact-label correctness is **1**, and Brier loss is **(0.25 - 0)^2 = 0.0625**. The correct modal call does not establish that its probability was calibrated.

The prediction freezes Term 2025, `elevated`, and `sal-v4`. The committed `metrics/statpack.md` heading matches that version, so the baseline uses the bracketed **reached** rates, with `base_rate_basis = risk_set`, not terminal-band rates or the evaluator's decided-docket context. Every displayed prior Term is included: 2017 through 2024. In ascending Term order, the displayed rate/weighted-denominator pairs are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336. Their resolved-weighted average is **484.386 / 2,810 = 0.17237935943060498**. The numerator is a sum reconstructed from rounded published percentages, not an observed integer grant count. The caption renders 10 of 10 pack Terms; only eight precede this prediction's Term. There is no hidden-window or salience-version mismatch.

The baseline's loss on this denial is the square of that rate. Thus skill is **1 - 0.0625 / 0.17237935943060498^2 = -1.1033400544962043**. This is a single-cell comparison, not an aggregate performance claim. The calculation uses the committed pack available to this evaluation, without a live corpus refresh or claim about current remote-corpus freshness.

## Reasoning quality: 0.65

The rationale appropriately anchors near the reached-band rate, recognizes the requested response and supporting amici as attention signals, and distinguishes two distribution entries from two completed substantive conferences. It preserves denial as the modal forecast rather than treating issue salience as enough for review. These are useful, case-specific reasons for its estimate.

Its treatment of the central conflict is less discriminating. It initially calls the split claimed but later describes it as cleanly presented without testing the opposition's principal response. The provisioned BIO, pp. 19–23, disputes whether the methodological difference would produce a different outcome for this slogan and emphasizes the lower court's characterization of its meaning as plainly vulgar. The rationale's generic fact-bound caveat does not develop that distinction. It also omits the BIO's qualified-immunity vehicle argument and the need to distinguish damages from prospective relief. The supplied QP is an advocate's framing, not independent confirmation of a clean split. The log shows a QP read but no substantive petition or BIO read.

The upward adjustment to 25% is intelligible but not quantitatively supported beyond those signals. Its reference to pooling ten prior Terms is imprecise: the relevant displayed pre-2025 window has eight. This is a reproducibility limitation, not evidence of a wrong approximate 17% anchor. The grade measures the rationale's balance and evidentiary discipline, not its brevity, correct label, or the Court's undisclosed reasons for denying review. The outcome supplies no explanation establishing that any particular vehicle objection caused denial.

## Leakage and scoring boundaries

The harness log labels the prediction forward. Its September 16, 2026 calls precede the October 5 resolution. Queries concern local inputs and a general student-speech corpus search, not this case's eventual disposition. The retrieval note acknowledges an unsuccessful query attempt despite the rationale's shorter statement that it used no external retrieval. All 26 results are marked `unobserved`; their missing dates and digests are not evidence that nothing returned. Timing, query content, and the prose provide no affirmative indication of outcome material or a mis-provisioned decided case. Accordingly, retrieved outcome material is false on the available evidence, influence is `not_applicable`, and leakage is not suspected.

I read the forecast document for context only. Neither it nor the quantitative claims enters reasoning quality. Claim scores are left to the harness. Vote accuracy and semantic grades are absent because this is a cert event. Optional significance scoring is omitted.
