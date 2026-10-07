# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage event. The outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot independently agrees within the supplied record. The predicted label is `denied`, giving **correct = 1**. The 0.012 grant probability yields Brier loss `(0.012 - 0)^2 = 0.000144`.

The frozen prediction context gives Term 2026, baseline band, and sal-v4. The corresponding committed sal-v4 table supplies the bracketed reached population, so `base_rate_basis = risk_set`. Pooling all displayed prior Terms, OT2017–OT2025, gives weighted denominator 12,720 and approximate weighted grant numerator 637.385: `segment_base_rate = 0.050108883647798745`. This calculation uses rounded published percentages and does not represent an exact integer grant count. The table renders 10 of 10 Terms, including the excluded current Term, so no rendered-window truncation flag applies. Baseline loss is approximately 0.002510900220428632; skill is `1 - 0.000144 / baseline_loss = 0.9426500508349878`. The figures describe the committed pack's denial-reweighted live/historical slice, not current remote-corpus freshness or an independently validated population forecast.

## Reasoning quality: 0.92

The rationale makes the information boundary and provenance clear. It attributes disputed facts and the lower court's reasoning to the supplied petition instead of claiming to have independently inspected the missing appendix. Its discussion of the employment agreement versus actual commencement of practice tracks the uncertainty visible in the petition, including the reproduced appellate discussion on printed pages 35–37. It separates a potential state eligibility violation from the additional argument needed for a federal constitutional claim, rather than assuming the former automatically proves the latter.

The doctrinal distinction is soundly grounded: the majority's discussion in Caperton v. A. T. Massey Coal Co., 556 U.S. 868, 876, 887–90 (2009), distinguishes ordinary disqualification issues from the exceptional constitutional threshold. I checked the relevant majority passages through CourtListener, opinion 9435330. The rationale also treats procedural dismissal, preservation, and finality as unresolved vehicle concerns rather than conclusively deciding them from the petitioner's account. Its treatment of the Maryland fee decision is similarly appropriately limited.

The statistical discussion selects the correct frozen risk-set band, matching version, and prior-Term window, and openly distinguishes rounded estimates from exact counts. It does not mistake terminal relist/CVSG strata for forward transition probabilities. The reduction from roughly 5% to 1.2% is transparently judgmental and tied to record-specific weaknesses, while preserving a residual chance for a cleaner constitutional issue than the incomplete materials reveal.

The remaining limitation is quantitative: there is no validated conditioned model or comparable sample establishing that these considerations warrant exactly 1.2%. The record remains one-sided and leaves the underlying employment facts unresolved. The high grade rewards disciplined analysis and uncertainty management, not the realized denial, and is not a claim that the Court adopted the forecast's reasoning. Only `reasoning.md` is graded; the predicted-reasoning document and mechanical claims contribute no separate qualitative score.

## Leakage and scope

The harness log marks forward. The October 4 prediction and tool activity precede the recorded October 5 denial. Twenty-five of 27 calls have captured results. The two unobserved web rows concern general review standards and Rule 10; their absent digests/dates do not prove empty results. The candidate reports no usable web content, but I independently rely on the visible non-case-specific queries rather than treating that report as captured evidence. Other calls concern provisioned documents, the statpack, and Caperton, not a later disposition of this petition. No outcome material is shown, so influence is `not_applicable` and leakage is not suspected. The evaluator's later snapshot is not used to infer what the predictor could see.

Cert-stage vote accuracy and semantic grades are omitted. Mechanical claim scores and provenance are left to the harness. I omit an independent stakes score because the candidate's own assessment had already been encountered.
