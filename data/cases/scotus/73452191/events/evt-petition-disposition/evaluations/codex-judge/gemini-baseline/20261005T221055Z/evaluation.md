# Evaluation: gemini-baseline

## Outcome and mechanical scores

This is a cert-stage petition-disposition event. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. gemini-baseline predicted `denied` with P(any grant) = 0.012: exact-label correctness is **1**, and Brier loss is **0.000144**. These numbers measure the recorded forecast against the outcome; the denial does not establish why the Court declined review.

## Baseline and skill

The prediction freezes Term 2025, band `baseline`, and version `sal-v4`. The committed statpack's heading matches that version. I use the bracketed baseline `reached` rates, not the leading terminal-band figures and not this evaluator's terminal context. The strictly prior rows are OT2024 5.7%/1271, OT2023 5.9%/1312, OT2022 5.8%/1192, OT2021 5.6%/1500, OT2020 4.5%/1739, OT2019 4.6%/1399, OT2018 4.6%/1524, and OT2017 4.7%/1643, where each pair is rate/weighted resolved denominator.

Pooling those displayed rates over n = 11,580 gives **0.05120250431778929**, on the `risk_set` basis. The baseline loss is that rate squared; skill is **0.9450737326637661**. This is approximate reconstruction from rounded, denial-reweighted published figures, not an exact count-derived rate. The table renders all 10 of its 10 Terms; 2025 and 2026 are excluded. There is no rendered-window truncation to flag. No live corpus was queried or refreshed, and no corpus-wide freshness claim is made. The prediction's snapshot date is September 15; the evaluator's supplied snapshot is October 5, 2026.

## Reasoning quality: 0.55

The rationale correctly starts near the prior-Term risk-set anchor and recognizes the waiver and absence of a response request as reasons for caution. It treats the asserted split as purported rather than established and allows some prospect of a later response request. Its low grant forecast is consistent with the outcome.

The analysis is nevertheless too dependent on the respondent's waiver to support the precision of its adjustment. It does not address the substantial preservation obstacle described in the petition, printed pages 9–10 and 19–21, or the petition's discussion of the competing Mireles analogy. Those are available, case-specific reasons to discount the asserted conflict. The respondent's assessment is not itself the Court's assessment.

There is also an identifiable baseline error in the rationale: the cited zero-relist 1.2% is the statpack's `granted` component alone; the same row adds 0.5% GVRs. The headline probability covers the grant family. Moreover, a terminal zero-relist group is not a forward transition rate for a petition merely awaiting its first conference. Neither issue changes the mechanical Brier calculation, but both weaken the probability justification. A correct denial forecast does not cure those analytical limitations.

## Leakage and scope

The harness log says `forward`, with all 29 calls dated September 16, before the supplied October 5 resolution. Its capture coverage is 0.0: every result is unobserved. I therefore do not infer unsuccessful or empty searches from null dates, digests, or the `unobserved` status. The logged corpus and caption queries and the candidate's prose show no disposing order, known result, or reliance on this petition having already been decided. The appropriate assessment is no observed outcome material, `not_applicable` influence, and `leakage_suspected = false`, with the capture limitation expressly retained.

Only `reasoning.md` is qualitatively scored. The forecast document was read for context, not scored; quantitative claims remain for the harness. No vote accuracy or semantic grades are written on this cert cell. No independent big-case score is supplied.
