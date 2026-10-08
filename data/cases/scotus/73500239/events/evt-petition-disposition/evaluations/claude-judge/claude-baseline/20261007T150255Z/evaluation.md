# Evaluation of claude-baseline — scotus/73500239, evt-petition-disposition

**Cell:** cert stage, forward mode. **Outcome:** petition denied on the October 5, 2026 order list after a single distribution for the September 28, 2026 conference; no CVSG, no relist, no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`, `noted_dissent_from_denial: false`).

## Scores

- **correct = 1.** Predicted `denied`; actual `denied`.
- **brier_score = 0.0004.** P(grant) 0.02 against actual 0.
- **segment_base_rate = 0.0512, base_rate_basis = risk_set.** The prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, matching the heading of the committed `metrics/statpack.md` band table. Pooled the bracketed `reached` baseline figures, resolved-weighted, over the rendered Terms strictly before OT2025 (OT2017–OT2024; denominators 1271, 1312, 1192, 1500, 1739, 1399, 1524, 1643 at 5.7, 5.9, 5.8, 5.6, 4.5, 4.6, 4.6, 4.7 percent), giving ≈ 5.12% over n = 11,580. The caption reports 10 of 10 Terms rendered, so no lookback divergence. Approximate to the table's rounding.
- **brier_skill_score = 0.8474.** 1 − 0.0004 / (0.0512 − 0)².
- **reasoning_quality = 0.9.**
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; `claim_scores` is the harness's.

## What the reasoning got right and wrong

The strongest rationale of the three. It anchors on the correct strictly-prior reached-baseline pool (5.1%, matching mine), then gives four ranked downward adjustments, each tied to a verifiable fact in the staged record: the respondents' waiver (correctly named the single largest factor); an unpublished Sixth Circuit affirmance on causation that never reached the Garcetti ground; a split the petition itself concedes is "not quite posed as it is here" and a proposed Sullivan-threshold rule no cited circuit has adopted; and a presentation that reargues the record and asks for a grant "whether the Court affirms or reverses." I checked each of those quotations and characterizations against `petition.txt` and they hold. The modest upward factor, the Garcetti reservation and Justice Thomas's MacRae statement cited in the petition, is the right one to name and is correctly weighted as a reason to stay at 2% rather than 1%.

Two things distinguish it from codex-baseline beyond the better calibration. First, it went looking for the opinion below and the Supreme Court docket on CourtListener, found neither indexed, and then said exactly what that means: its vehicle read rests on an advocate's account, with a stated reason to believe that account (consistency across the petition's sections, and a waiver consistent with a respondent who reads the holding as fact-bound). Second, the closing "Where to discount me" section states what would supersede the forecast (a call for a response) and what the number is really made of (two docket facts and a base rate). That is the right epistemic posture for a waived-response petition. The relist reasoning is also unusually careful, noting that the terminal relist shape includes petitions with filed oppositions and so overstates the hazard for a waived one.

The only reservations are small: the corpus query it ran returned nothing comparable and served no analytic purpose, and the "solo practitioner" point is more a heuristic than an argument. Hence 0.9.

## Leakage

Mode `forward`. The prediction was created September 17, 2026, before the conference and the denial. `result_capture_coverage` is 1.0, so every result was seen. Four CourtListener searches named this case's caption (Pesta, Cleveland State University, Bloomberg); three returned nothing and the fourth returned the N.D. Ohio district docket dated 2023-03-16, the pre-petition procedural history. A corpus query for granted 2020s rows carries a latest document date of 2025-02-11 and touched no row for this case. Searching an open docket's own caption in forward mode is the ordinary forward shape, not leakage, and the rationale discloses the searches and that nothing revealed the disposition. No web search, no read under `data/qp-topics/`. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. No evidence of a decided case provisioned forward.

## Big case

My independent read is 0.2 (see `big_case.notes`). The predictor's own score sits in the staged `prediction.json`, so it was visible when I read the record; the read above is my own, formed from the posture, the waiver, and the silent denial.
