# Evaluation: claude-baseline

## Outcome and numerical scores

The cert-stage outcome records `denied` and `actual_granted = 0` on October 5, 2026. claude-baseline's denial label is correct, giving correctness 1 and Brier loss `(0.005 - 0)^2 = 0.000025`.

The prediction froze Term 2025, `baseline`, and `sal-v4`. The matching committed statpack table supplies bracketed reached rates, pooled resolved-weighted over all shown strictly prior Terms, 2017–2024. In descending Term order the rate/count pairs are (5.7%, 1271), (5.9%, 1312), (5.8%, 1192), (5.6%, 1500), (4.5%, 1739), (4.6%, 1399), (4.6%, 1524), and (4.7%, 1643). Their denominator is 11,580 and their pooled rate is 0.05120250431778929, on the `risk_set` basis. These are denial-reweighted live/historical-slice estimates reconstructed from rounded published percentages, not exact underlying counts. The caption shows all 10 of 10 Terms; neither Term 2025 nor 2026 enters the pool, and no rendered-window divergence exists. Baseline loss is approximately 0.002621696448413231, yielding skill 0.9904641896985705. This single-event result establishes neither calibration nor population skill. I use the committed pack, without claiming a fresh corpus observation.

## Reasoning quality: 0.65

The analysis identifies a plausible denial rationale: a localized, fact-bound evidentiary dispute with no demonstrated conflict, despite the petition's federal framing. It reads the full petition, recognizes the state appellate origin, and correctly constructs the pooled prior-Term anchor. Its stated probability range makes some uncertainty visible.

Several categorical assertions exceed the evidence it describes. The statement that no opposition was provisioned because none was filed, and that the city had not engaged, cannot be established from an incomplete docket or an endpoint returning no entries; the candidate's later acknowledgement that it could not confirm intervening filings does not resolve those assertions. Calling the case one with an adequate and independent state ground is stronger than the petitioner's account of record-support deficiencies establishes without the lower-court opinion. The asserted explanation for the originating-court GVR share is not demonstrated by the aggregate rate cited. Two truncated, disposition-selected corpus queries cannot establish a representative counsel comparison or quantify the probability adjustment. Finally, a reached-band anchor already includes petitions at the present weak posture, so lack of future escalation is not by itself an additional measured downward effect.

Those weaknesses concern evidentiary discipline in `reasoning.md`, not the separately forecast claims. The correct denial does not retrospectively establish the categorical jurisdictional or procedural assertions, and the supplied outcome gives no reasons for denial. The grade therefore remains materially below what outcome accuracy alone would suggest.

## Leakage and scoring boundaries

The forward log has 100% result-capture coverage. The prediction and calls are dated September 16, before the recorded October 5 resolution. Its case-specific CourtListener request was legitimate forward retrieval; the staged retrieval note reports zero entries, not discovery of a disposition. Corpus comparisons concern other denied and granted cases, and the visible document date is February 11, 2025. No record or prose reveals this case as already decided when predicted. Thus influence is `not_applicable` and leakage is not suspected. The captured transcript's digests are not full result bodies, so this is an evidence-based assessment, not an assertion of omniscient verification.

The original prediction snapshot is not staged here, and the evaluator's later snapshot is not treated as proof of its earlier contents. The forecast document is context only and remains unscored. Quantitative claim scoring is reserved to the harness; cert vote accuracy and semantic grades are omitted. No optional independent stakes score is supplied.
