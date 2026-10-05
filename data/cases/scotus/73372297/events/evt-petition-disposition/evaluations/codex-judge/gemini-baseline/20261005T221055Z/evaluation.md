# Evaluation: gemini-baseline

## Outcome and numerical scores

The cert-stage outcome records denial on October 5, 2026, with `actual_granted = 0`. gemini-baseline's September 16 prediction names `denied` with grant probability 0.001: `correct = 1`, and `(0.001 - 0)^2 = 0.000001`. This is the smallest realized Brier loss among the three staged candidates, not evidence that its reasoning is strongest or its probabilities generally calibrated.

The scored baseline comes from the prediction's frozen Term 2025, `baseline` band, and `sal-v4` version, which matches the committed statpack heading. It is a `risk_set` baseline. The strictly prior rendered rows are 2024: 5.7%, n=1,271; 2023: 5.9%, n=1,312; 2022: 5.8%, n=1,192; 2021: 5.6%, n=1,500; 2020: 4.5%, n=1,739; 2019: 4.6%, n=1,399; 2018: 4.6%, n=1,524; and 2017: 4.7%, n=1,643. Pooling those bracketed reached rates gives 592.925 / 11,580 = 0.05120250431778929. The numerator reflects rounded displayed percentages, not an integer outcome count. The table renders all 10 of its 10 Terms; excluding 2025 and 2026 creates no display-window divergence. Skill is `1 - 0.000001 / 0.05120250431778929^2 = 0.9996185675879429`.

The rationale's claimed “prior-Term” 3.9% anchor is not that pool. It matches the displayed 2025 reached rate, which is the prediction's own Term, not a strictly prior one. This is a reproducible baseline-selection error, recorded in the cell-level flags. The evaluation uses the correct pool rather than propagating the error. Forward access to current aggregate statistics is not itself outcome leakage; mislabeling that rate affects analytical quality, not the mathematical Brier loss.

The baseline is the committed statpack's denial-reweighted live/historical-slice estimate, not a fresh corpus query. The inspected pack supplies no corpus-wide pull vintage; no case-specific last-pulled timestamp was supplied. The evaluation snapshot is dated October 5, 2026, whereas the prediction context identifies September 16. No claim about current remote-corpus freshness is made.

## Reasoning quality: 0.48

The rationale identifies two useful observations: an initial distribution without additional attention and the federal respondent's response waiver. Its conclusion that the questions presented do not develop a strong review vehicle is directionally consistent with the supplied questions and the realized denial.

However, the headline analysis mainly labels the allegations “manifestly frivolous” and “incoherent,” rather than identifying which legal issue or procedural obstacle makes this petition a poor vehicle. The staged petition expressly discusses a disputed lower-court review deadline, but that issue is not analyzed. The log shows a questions-presented read and no full petition read; the absence of full reading is not a standalone penalty, but the omitted procedural analysis is visible in the rationale itself. A waiver supplies an observed signal, not an adjudication that the allegations lack merit. The erroneous 3.9% prior-Term claim also weakens the numerical foundation, and the jump to 0.1% lacks a developed explanation of its magnitude or residual uncertainty.

The score is not a penalty for brevity. It reflects the inaccurate anchor and the missing analytical bridge between asserted frivolousness, the actual review posture, and the probability. The unexplained denial does not establish that the allegations were false or that the Court adopted any particular rationale. Only `reasoning.md`'s headline analysis is graded: the forecast document and the increment/conditional claims are not folded into this score.

## Leakage and scoring boundaries

The harness identifies a forward prediction. Its 20 calls all have `result_capture = unobserved` and coverage 0.0. This is a limitation of the captured evidence, not proof of empty results, not a tool failure, and not a defect to penalize. Recorded queries read the September 16 context, snapshot, questions presented, document manifest, statpack, and schemas, then create and validate outputs. They show no external or own-case outcome search. The prediction date precedes the October 5 resolution, and its prose presents denial as a forecast, not an already-known fact. On that evidence, outcome material is assessed false and influence `not_applicable`, with suspected leakage false; uncaptured results prevent stronger claims about precisely what each read returned.

Cert vote accuracy and semantic grades are omitted. Mechanical claim scores remain the harness's responsibility. No independent big-case score is supplied because the required reading exposed candidate significance judgments before an independent assessment was fixed.
