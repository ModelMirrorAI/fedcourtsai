# Evaluation: claude-baseline

## Outcome and numerical scores

The cert-stage event resolved as denied on October 5, 2026, with `actual_granted = 0`. claude-baseline's September 16 prediction named denial and assigned P(any grant) = 0.005. Correctness is 1; Brier is `(0.005 - 0)^2 = 0.000025`.

The scoring baseline comes from the prediction's frozen Term 2025, `baseline` band, and `sal-v4` version, not from the evaluator's terminal context. The statpack's matching table supplies prior-Term reached rates and weighted resolved denominators: 2024 (5.7%, 1271), 2023 (5.9%, 1312), 2022 (5.8%, 1192), 2021 (5.6%, 1500), 2020 (4.5%, 1739), 2019 (4.6%, 1399), 2018 (4.6%, 1524), and 2017 (4.7%, 1643). The weighted sum is approximately 592.925 grants over 11580, giving 0.05120250431778929. This is a denial-reweighted estimate from rounded displayed percentages. The table renders 10 of 10 Terms; all eligible displayed rows are included, and this case's own Term and later rows are excluded. No window or salience-version mismatch applies. No fresh corpus state is claimed.

With `base_rate_basis = risk_set`, skill is `1 - 0.000025 / 0.05120250431778929^2 = 0.9904641896985705`. The rationale's denominator of 11680 is a small arithmetic error: its own listed rows sum to 11580. Its approximate 5.1% anchor is nevertheless close. Scoring uses the independently computed value, not that typo. One successful denial forecast does not establish calibration.

## Reasoning quality: 0.78

The rationale provides a substantive, case-specific account of the COA posture, the distinction between Wisconsin self-defense law and the asserted federal burden-of-proof issue, the undeveloped conflict claim, and the limited record. It recognizes that a first long-conference distribution is not itself a relist. Its decision to use a strictly-prior risk-set anchor is sound, and its discussion of the missing appendix limits the certainty of its account.

Several assertions are more categorical than the supplied support warrants. Statements that the Court grants almost no COA-denial petitions or overwhelmingly favors state petitioners are not supported by a matched empirical comparison in the retrieved materials. An instruction directing consideration of self-defense and an allegation that the jury failed to follow it are not logically inconsistent, contrary to the drafting critique. The different warden caption and pro se presentation do not independently establish the weakness of a federal claim. The response waiver is relevant posture, but attributing a definite merits judgment to the respondent overstates what the entry itself shows. These issues, plus the small pooling error and judgmental probability adjustment, prevent a higher score despite the useful analysis.

The denial validates the label forecast, not these substantive explanations: the outcome supplies no reasoned ruling on the petition's allegations.

## Leakage and scoring boundaries

The prediction is forward. All 26 logged calls have captured results and precede resolution. The candidate's current-docket and lower-court searches were permissible while the petition was pending. The log's May 13 and September 10 document dates predate the October 5 denial; the latter accompanies a generic query for other denied cases, not this petition's eventual result. The rationale and retrieval note describe no target disposition and acknowledge stale docket metadata. There is no evidence of a decided case provisioned forward. Outcome material is false, influence `not_applicable`, and leakage not suspected.

The forecast and quantitative claim block are not graded here or folded into reasoning quality; claim scores belong to the harness. Cert votes remain unscored, and no judgment or semantic grade applies. No independent big-case assessment is supplied.
