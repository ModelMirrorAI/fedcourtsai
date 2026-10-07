# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage disposition cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The staged September 17 prediction names `denied` and assigns any grant probability 0.07. Thus exact-label correctness is **1**, and the Brier score is **(0.07 - 0)^2 = 0.0049**. These numbers evaluate the disposition, not the constitutional merits.

The prediction froze Term 2025, band `elevated`, and salience version `sal-v4`. The committed `metrics/statpack.md` table bears the same version, so the baseline uses its bracketed **reached** figures, not terminal rates or the evaluator's decided-docket context. The strictly prior displayed Terms are 2017–2024. Their rate/weighted-n pairs, in ascending Term order, are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336. The executed calculation gives 484.386 / 2,810 = **0.17237935943060498**, and skill **1 - 0.0049 / baseline^2 = 0.8350981397274976**.

This is a denial-reweighted paid-segment estimate calculated from rounded displayed rates, not an exact grant count. The caption renders all ten Terms the pack holds; the case's own Term and 2026 are excluded. No shortened-rendering divergence applies. These are committed-pack inputs, not a claim about fresh corpus state; no corpus refresh or vintage lookup was performed. Positive skill describes this one grading, not aggregate predictive performance.

## Reasoning quality: 0.90

The probability rationale is specific, balanced, and well tied to the supplied materials. It identifies the petition's numerical-cap distinction rather than dismissing the constitutional challenge by label, then explains why the source-and-purpose and qualitative-constraint reasoning described in the opposition weakens that distinction. It distinguishes general doctrinal obstacles from a categorical conclusion that every agency's funding constraints necessarily suffice. The absence of an asserted circuit split supplies a separate certiorari consideration.

Its vehicle analysis is especially careful: standing, preclusion, and preservation are characterized as respondent objections, not adjudicated defects. That matches the opposition's account and the supplied petition appendix at 7a–10a, where the appellate court rejected the standing objection. The rationale also acknowledges petitioners' response on preservation and the unavailable reply. It correctly separates two distributions from two substantive conference considerations and does not treat a requested party response as a CVSG.

The main limitation is calibration: reducing the approximately 17.24% population anchor to 7% remains a reasoned judgment, not an estimated conditional rate. The available outcome records a denial, not the Court's reasons, so it cannot verify that any particular doctrinal or vehicle objection drove the result. The correct outcome therefore earns no automatic increase in this analysis-quality grade.

Only `reasoning.md` supplies the quality assessment. The pointed-to forecast was read for context, but its timing, writing, and other predictions are unscored here. Mechanical claim scores belong to the harness. No semantic set is graded on cert; cert votes are not scored.

## Leakage assessment

The harness log identifies a forward prediction and places all 37 calls on September 17, before the October 5 resolution. It captures 34 results; three web calls are unobserved. The latter seek general precedents from 2024 and 2025, not a later disposition of this petition. The other visible queries concern provisioned case inputs, committed rates, precedent passages, and output operations. The rationale explicitly treats the petition as awaiting the September conference and reports no known outcome.

No affirmative evidence indicates this petition was already decided when predicted. Accordingly, `retrieved_outcome_material` is false, influence is `not_applicable`, and suspicion is false. This is not a finding that the unobserved web calls returned nothing: their results are unavailable regardless of the candidate's self-report. Null document dates likewise do not prove absence. The evaluator's current snapshot is not used to reconstruct what the predictor received, and absent candidate flags are not treated as proof of cleanliness.
