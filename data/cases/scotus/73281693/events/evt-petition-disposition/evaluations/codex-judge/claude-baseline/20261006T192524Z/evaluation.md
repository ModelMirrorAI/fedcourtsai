# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage evaluation of the prediction from run `20260918T174135Z`. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. The predicted label was `denied`, so correctness is **1**. With P(grant) = 0.35, the Brier score is `(0.35 - 0)^2 = 0.1225`.

Use the prediction's frozen elevated band under sal-v4 and docket Term 2025, not the evaluator's terminal context. The committed `metrics/statpack.md` table matches sal-v4 and renders 10 of 10 Terms. Its eligible bracketed reached rates and weighted denominators are OT2024: 17.9%, 336; OT2023: 17.5%, 354; OT2022: 19.0%, 300; OT2021: 20.5%, 342; OT2020: 16.1%, 397; OT2019: 13.8%, 334; OT2018: 15.9%, 347; OT2017: 17.5%, 400. Neither the petition's own Term nor the subsequent Term enters the pool.

Pooling the displayed percentages gives `484.386 / 2810 = 0.17237935943060498`, basis `risk_set`. This fractional numerator reflects rounded published rates and denial reweighting, not a raw count of grants. Brier skill is `1 - 0.1225 / 0.17237935943060498^2 = -3.1225465068125605`. Thus the correct modal label coexists with a worse single-event probability score than the baseline. No conclusion about long-run calibration follows. These are estimates from the committed table; no live corpus refresh or freshness measurement was undertaken.

## Reasoning quality: 0.82

The rationale offers a substantive adversarial analysis. It recognizes the opposition's distinction between actual hardship supported by medical evidence and merely good-faith fears, discusses cross-citation between allegedly conflicting circuits, and identifies independent evidentiary objections. These are genuine features of the provisioned opposition, rather than explanations invented after denial. It also distinguishes redistribution after a response request from a conventional relist, uses the proper reached-band anchor, and candidly identifies limits of the missing reply, unexamined lower-court opinion body, and unhelpful retrieval.

The principal weaknesses concern the strength assigned to positive signals. Calling the question purely legal and outcome-determinative is too categorical alongside the acknowledged alternative evidentiary grounds. The claim that response-request petitions grant at a multiple of the docket rate is not backed by a relevant conditional estimate here, and its relevance over an already elevated-band baseline is not demonstrated. Counsel, organized amicus support, and perceived receptivity to religious accommodation plausibly matter, but the roughly doubled grant probability is not disciplined by a quantified incremental comparison. The rationale itself provides substantial reasons to doubt a clean conflict, yet the upward adjustment remains pronounced.

The grade rewards the actual legal and procedural analysis without turning this realized denial into proof that a 35% forecast was irrational. Nor does the denial establish the Court's reasons. The opening remark about event fields is not treated as a data defect: it describes the predictor's historical input, which is not independently reproduced by the evaluator's later event record. Only `reasoning.md` is graded; the separate forecast and mechanical claims remain outside this qualitative score.

## Leakage and scoring boundaries

The harness log records 40 captured calls, all on September 18, 2026, before resolution. It includes provisioned documents, the committed statpack, two corpus queries, and CourtListener searches for the lower-court decision and related accommodation litigation. The legible external document dates are September 2, 2025 and May 6, 2026. Those are pre-resolution lower-court materials, not this petition's October 5 denial. Searches for related petitions likewise are not evidence of exposure to this petition's disposition.

The reasoning says the corpus priors were not topically useful and discloses no knowledge of this petition's outcome. Captured-result digests are not full result bodies, but the logged queries, dates, and prose show no concrete already-decided own-case material. Mode is `forward`, retrieved outcome material is false, influence is `not_applicable`, and leakage is not suspected. The unstaged predictor flags are not used as evidence of cleanliness.

No cert vote accuracy or semantic grades are written. Mechanical claim scoring and provenance stamps remain harness-owned.
