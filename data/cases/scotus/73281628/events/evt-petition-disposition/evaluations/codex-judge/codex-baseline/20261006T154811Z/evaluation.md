# Evaluation: codex-baseline

## Outcome and numerical scoring

This is a cert-stage petition-disposition cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`, no noted dissent, and no recorded votes. codex-baseline's September 17 prediction names `denied`, so `correct = 1`. Its probability covers any grant, including the requested mootness GVR, rather than only plenary review. Brier loss is `(0.38 - 0)^2 = 0.1444`.

The prediction froze `elevated`, `sal-v4`, and Term 2025. These match the committed statpack's sal-v4 heading; the evaluator's terminal context is not used to choose the band. I pool the bracketed reached rates for every displayed Term strictly before 2025: 2017 17.5%/400; 2018 15.9%/347; 2019 13.8%/334; 2020 16.1%/397; 2021 20.5%/342; 2022 19.0%/300; 2023 17.5%/354; 2024 17.9%/336. The weighted numerator is 484.386 and denominator 2,810, giving `segment_base_rate = 0.172379359430605`, on the `risk_set` basis. These are denial-reweighted live/historical-slice estimates calculated from displayed rounded percentages, not exact grant counts. The table renders all 10 of its 10 Terms; 2025 and 2026 are excluded, so there is no rendered-window truncation to flag. This describes the committed pack, not a freshly queried corpus.

The baseline's loss on this denial is approximately 0.02971464356. Therefore `brier_skill_score = 1 - 0.1444 / 0.02971464356 = -3.8595568619080305`. The modal outcome was right, but the assigned grant probability loses more than the band baseline on this observation. This is a single-event comparison, not evidence of overall calibration or performance.

## Reasoning quality: 0.90

The rationale distinguishes the narrow mootness-vacatur request from the underlying sentencing and habeas controversy, treats the petition's constitutional assertions as advocacy, and separates mootness of the underlying controversy from disposition of the pending petition. Its discussion of the provisioned petition and opposition recognizes both the petitioner's efforts to preserve review and the government's substantial voluntary-mootness, jurisdictional-dismissal, and independent-certworthiness objections. It does not convert the government's disputed positions into categorical law or confuse disagreement within a panel with a demonstrated circuit conflict.

The analysis also correctly avoids reading two distributions as two completed conferences and explains the limited signal in the response request. It uses the frozen, version-matched, strictly-prior risk-set anchor and explicitly distinguishes pooled descriptive figures from transition probabilities. Its additional account of the reply is supported by logged retrieval of that fixed predecision document; I have not independently fetched the reply or the cited authority. The reasoning is appropriately conditional about the equitable balance rather than treating vacatur as automatic.

The principal limitation is quantitative: the rise from approximately 17.24% to 38% is a transparent but unvalidated judgmental adjustment, not an estimate supported by a matched mootness-vacatur subgroup. Strong argument analysis does not validate that magnitude. The unexplained denial cannot establish which equitable or certworthiness argument the Court accepted. This quality score concerns `reasoning.md` only; it neither rewards correct forecast details nor imports scores for the claims or forecast document.

## Leakage and scope

The captured log marks this prediction `forward`. Its calls and prediction date are September 17, before the October 5 resolution. The external query slices concern a 2018 vacatur authority and the exact August 5 reply linked in the baseline. No query or passage shows Bell's Supreme Court disposition already known. Coverage is 27 captured calls out of 29. The two web calls are explicitly unobserved: I do not adopt the candidate's claim of empty results as independently established, and I do not treat their null dates as proof of nonretrieval. Their recorded targets are nevertheless preexisting authority, not this petition's outcome. Accordingly, outcome-material retrieval is false on the available evidence, influence is `not_applicable`, and `leakage_suspected` is false.

Votes are unscored because this is cert, and no semantic set applies. The forecast document was read only for context. Mechanical claim scores and provenance stamps are left to the harness. No independent big-case assessment is supplied.
