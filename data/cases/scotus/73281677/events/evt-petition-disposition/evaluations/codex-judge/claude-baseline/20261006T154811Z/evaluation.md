# Evaluation: claude-baseline

## Outcome and numerical scores

This is a cert-stage petition-disposition cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. claude-baseline's September 16 forecast names `denied` and assigns 0.015 to any grant. Thus `correct = 1` and Brier loss is `(0.015 - 0)^2 = 0.000225`. The denial establishes the outcome label, not the Court's reasons for denying review.

The baseline uses this prediction's frozen `context.band = baseline`, `salience_version = sal-v4`, and Term 2025, not the evaluator's post-decision context. The committed statpack's matching sal-v4 table supplies bracketed **reached** rates. The strictly-prior rows used are:

| Term | Reached rate | Weighted resolved n |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Resolved-weighted pooling gives 0.05120250431778929 over weighted n = 11,580. This is an approximation from rounded displayed rates, on the pack's paid, denial-reweighted live/historical slice, not reconstructed exact grant counts or a fresh corpus census. The caption renders all 10 of 10 available Terms; excluding 2025 and 2026 leaves these eight, with no rendered-window discrepancy. No corpus lookup or freshness claim is made. `base_rate_basis = risk_set`; baseline loss is approximately 0.002621696448413231 and skill is `1 - 0.000225 / baseline_loss = 0.9141777072871345`. This is a single-cell comparison, not evidence of aggregate calibration or forecasting skill.

## Reasoning quality: 0.83

The rationale identifies a strong case-specific reason to move below the prior-Term anchor: closely analogous denials already described in the parties' briefs, especially Schneider's consolidated petition. It separates the military appellate-review gateway from the underlying firearms merits, discusses the sparse decisions below, recognizes the government's opposition and changed indorsement practice, and acknowledges the unread reply and uncertainty about Zhong. The anchor uses the correct frozen band and risk-set population, rather than treating a federal respondent as a federal petitioner. These are substantive strengths independent of the successful disposition call.

Several qualifications keep the score below the strongest analysis. The assertion that no split is possible because CAAF is the only appellate court reading Article 66(d)(2) is too sweeping: the materials themselves concern military courts of criminal appeals applying that provision. The narrower supported point is that the record identifies no competing appellate holding on the immediate review question; the petition separately discusses a civilian firearms split (petition p. 19 n.6). The rationale's withdrawal/mootness framing understates the temporary memorandum and asserted continuing injury, both acknowledged in petition p. 10 n.2 and opposition p. 10. Also, its drug-user-law residual does not clearly connect an intervening merits ruling to this jurisdictional vehicle; petition p. 16 n.3 says the annotation specifies no subsection and assumes section 922(g)(1). Finally, the 1.5% adjustment is an informed judgment, not an estimated likelihood ratio. The denial does not independently validate these disputed premises.

Only `reasoning.md` receives this quality score. The separate court forecast was read for context, not graded; quantitative claims remain for the harness. Votes are not scored on cert cells, and no semantic-grades block is applicable. No independent big-case score is supplied.

## Leakage assessment

The captured log labels the prediction forward and dates its 34 calls to September 16, 2026, before the recorded October 5 resolution. Capture coverage is 1.0. I reviewed the query slices, result statuses and dates, retrieval note, and both prose documents. They include searches and metadata retrieval for this docket, companion cases, and a generic corpus query for granted cases; none evidences this petition's later denial. Legible result dates precede resolution, while the prose consistently treats Myslow as pending. A null termination value alone would not prove pendency; the chronology and absence of outcome-presupposing reasoning support the assessment together.

The January denials concern other petitions and were legitimate forward information. The forecast's anticipated October order-list timing is a forecast, not evidence that the later result was retrieved. The evaluator's October 5 snapshot is not treated as the predictor's input. Recorded result digests and truncated query slices are not full response bodies, so this is an assessment of the available audit evidence, not a claim of omniscient inspection. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. No forward mis-provisioning or other issue requiring a flag was found.
