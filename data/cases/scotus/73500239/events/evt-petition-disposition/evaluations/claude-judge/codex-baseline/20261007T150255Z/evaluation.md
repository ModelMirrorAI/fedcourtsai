# Evaluation of codex-baseline — scotus/73500239, evt-petition-disposition

**Cell:** cert stage, forward mode. **Outcome:** petition denied on the October 5, 2026 order list after a single distribution for the September 28, 2026 conference; no CVSG, no relist, no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`, `noted_dissent_from_denial: false`).

## Scores

- **correct = 1.** Predicted `denied`; actual `denied`.
- **brier_score = 0.0009.** P(grant) 0.03 against actual 0.
- **segment_base_rate = 0.0512, base_rate_basis = risk_set.** The prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, matching the heading of the committed `metrics/statpack.md` band table. Pooled the bracketed `reached` baseline figures, resolved-weighted, over the rendered Terms strictly before OT2025 (OT2017–OT2024; denominators 1271, 1312, 1192, 1500, 1739, 1399, 1524, 1643 at 5.7, 5.9, 5.8, 5.6, 4.5, 4.6, 4.6, 4.7 percent), giving ≈ 5.12% over n = 11,580. The caption reports 10 of 10 Terms rendered, so no lookback divergence. Approximate to the table's rounding.
- **brier_skill_score = 0.6567.** 1 − 0.0009 / (0.0512 − 0)².
- **reasoning_quality = 0.85.**
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: not applicable on a cert cell; `claim_scores` is the harness's.

## What the reasoning got right and wrong

This is a careful, well-conditioned rationale. It reads the full petition, pools the correct strictly-prior reached-baseline anchor (its 5.12% matches mine), and identifies the decisive vehicle facts from the petition's own procedural history: the Sixth Circuit affirmed on retaliatory causation and did not explicitly reach the district court's alternative Garcetti ground, so a win on the academic-speech question would not necessarily disturb the judgment. I verified those passages in the staged petition. It also catches the petition's concession that the cited Johnson v. Multnomah County disagreement is not the across-the-board actual-malice rule the petition proposes, and it tests the one doctrinal premise it relies on (Garcetti's reservation of scholarship and teaching) against the opinion text via CourtListener. Its handling of uncertainty is exemplary: it separates the snapshot's filename date from its last-proceeding date, declines to treat the petition's record characterizations as fact, and says plainly that no opposition existed to test them.

The reservation is calibration rather than analysis. Having found a waived response, an unpublished causation affirmance, no square split, and a solo-practitioner petition that reargues the record, the rationale still lands at 3%, above the other two candidates and only modestly below the band pool. The "substantial subject-matter importance" it credits upward is real as a doctrinal matter but is the kind of interest that produces a call for a response before a grant, and no such call had issued. The document also spends a paragraph on terminal relist and CVSG shape tables it then rightly declines to use, which is honest but adds little. Hence 0.85: thorough, accurate, well-sourced, and slightly under-decisive on the signals it had assembled.

## Leakage

Mode `forward`. The prediction was created September 17, 2026, before the conference and the denial. `result_capture_coverage` is 0.88. The three unobserved rows are web searches for the Court's Rule 10 and Rule 15 filing guidance, graded on their queries, which name neither this case nor any docket. The captured CourtListener calls fetched Garcetti v. Ceballos (547 U.S. 410) and its page-425 passage. The corpus CLI was used only to resolve output paths. No read under `data/qp-topics/`. The rationale states no disposition was known or retrieved, and the log agrees. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. No evidence of a decided case provisioned forward.

## Big case

My independent read is 0.2 (see `big_case.notes`). The predictor's own score sits in the staged `prediction.json`, so it was visible when I read the record; the read above is my own, formed from the posture, the waiver, and the silent denial.
