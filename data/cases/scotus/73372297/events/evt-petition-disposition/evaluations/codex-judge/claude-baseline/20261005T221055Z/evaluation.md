# Evaluation: claude-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition event. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`; the provisioned October 5 snapshot also records “Petition DENIED.” The September 16 prediction names `denied` and assigns any grant probability 0.004. Therefore `correct = 1` and Brier loss is `(0.004 - 0)^2 = 0.000016`.

The prediction's own frozen context is Term 2025, `baseline`, `sal-v4`. The committed statpack's salience heading matches that version, so the appropriate basis is `risk_set`, not terminal banding and not the evaluator's post-decision context. Pooling the displayed bracketed baseline reached rates over every rendered Term strictly before 2025 gives:

| Term | Reached rate | Weighted resolved n |
| --- | --- | --- |
| 2024 | 5.7% | 1,271 |
| 2023 | 5.9% | 1,312 |
| 2022 | 5.8% | 1,192 |
| 2021 | 5.6% | 1,500 |
| 2020 | 4.5% | 1,739 |
| 2019 | 4.6% | 1,399 |
| 2018 | 4.6% | 1,524 |
| 2017 | 4.7% | 1,643 |

The resolved-weighted mean is 592.925 / 11,580 = 0.05120250431778929. The numerator is a weighted sum of rounded published rates, not an integer grant count. The table renders 10 of 10 Terms; 2025 and 2026 are excluded, and there is no hidden-window discrepancy. The skill score is `1 - 0.000016 / 0.05120250431778929^2 = 0.9938970814070851`. The companion JSON's unrounded fields give 593 / 11,580, explaining codex-baseline's slightly different figure; this evaluation consistently uses the prescribed Markdown table.

These are denial-reweighted live/historical-slice estimates from the committed statpack available to this run, not a newly queried corpus. No corpus-wide pull vintage or case-specific last-pulled timestamp is supplied in the inspected inputs. The case snapshot is dated October 5, 2026; that is not a corpus freshness attestation. This one realized loss and skill score do not establish calibration or population-level forecasting performance.

## Reasoning quality: 0.78

The rationale identifies concrete, relevant features rather than merely picking the common label: an individualized compensation dispute, the petition's account of an untimely request for lower-court review, the government's response waiver, and a single distribution without an observed response request. The petition's “The Appeal” and “Reasons for Granting” sections support characterizing the requested intervention as predominantly record-specific correction. The prior-Term risk-set calculation is transparent and approximately correct, and the nonzero probability acknowledges residual uncertainty.

The analysis nevertheless overstates some premises. Its asserted near-zero empirical grant rate for paid pro se petitions is unsupported by a cited matching stratum. Its descriptions of the lower-court order as nonprecedential and of the procedural bar as established outrun the supplied petition-only account; the linked appendix and lower-court decisions are not staged. “No legal question” is stronger than “no developed conflict or clean review vehicle,” and the categorical assertion that no relevant intervening authority exists is not established by the disclosed retrieval. Those limitations justify a material deduction despite the correct denial prediction.

The outcome supplies no explanation of the Court's reasons, so it does not prove those analytical premises or adjudicate the petitioner's allegations. The score grades the headline-probability analysis in `reasoning.md` only. The forecast document was read for context; its timing, procedural predictions, significance discussion, and the structured claims receive no independent reward or penalty here.

## Leakage and scoring boundaries

The harness log reports `forward` and 23 of 23 calls with captured results. All calls precede resolution, on September 16. The sole corpus lookup is a generic search for recent grants, not a search for this petition's result; the candidate describes the returned priors as unhelpful. Other recorded queries read provisioned inputs and aggregate statistics or write and validate the candidate's own output. The prose describes the September 28 conference as future. There is no evidence that this case's October 5 disposition was retrieved or provisioned to the prediction. Accordingly outcome material is assessed false, influence `not_applicable`, and suspected leakage false. The prediction's original snapshot is not staged for the evaluator; this conclusion does not infer its contents from the evaluator's later snapshot.

No cert votes are scored, no semantic set is graded, and no mechanical `claim_scores` are supplied; those claims belong to the harness. No independent big-case score is supplied because candidate significance scores were encountered while reading the required rationale before an independent assessment was fixed.
