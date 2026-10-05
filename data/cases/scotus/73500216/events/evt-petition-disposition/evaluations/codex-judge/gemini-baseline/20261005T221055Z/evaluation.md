# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a cert-stage petition-disposition cell. The authoritative outcome records denial on October 5, 2026, with `actual_granted = 0`. The prediction's `denied` label matches exactly: correctness is **1**. With P(grant) = 0.01, the Brier score is **0.0001**.

The prediction froze Term 2025, band `baseline`, and version `sal-v4`. Those match the committed statpack's band-table version. I use the bracketed reached population, not the leading terminal rate or this evaluator's terminal context. The displayed strictly-prior rows are OT2017–OT2024. Their exact companion values in `metrics/statpack.json` pool to 593 / 11,580 = **0.05120898100172712**, matching the executed `prediction_base_rate` calculation. Thus `base_rate_basis` is `risk_set`, and skill is 1 - 0.0001 / baseline² = **0.961866406558813**. OT2025 and OT2026 are excluded. This is the committed pack's estimate, not a claim about freshly queried corpus state; no live corpus freshness was established.

## Reasoning quality: 0.55

The rationale identifies a plausible reason to move below the approximately 5.1% prior: the restrictive federal-habeas vehicle, a fact-sensitive juror-bias question, and the distinction between a concurrence and a controlling holding. Those are relevant pre-decision considerations. The successful denial call does not, however, validate every asserted premise.

Two substantial weaknesses reduce the grade. First, the rationale asserts that the respondent waived opposition, but no supporting waiver entry is identified. The provisioned docket has a response deadline and distribution, not a waiver; an absent opposition is not affirmative evidence of waiver. Second, the rationale treats the lack of clearly established implied-bias law as categorically dispositive. The petition's Appendix A, pp. 7a–9a, instead expressly assumes the doctrine is clearly established and rejects relief on the sparse facts, voluntary disclosure, and the state court's reasonable application. That alternative ground is materially more careful than the candidate's claim that relief cannot be available merely because the doctrine is associated with a concurrence. The 1% adjustment is plausible but not quantitatively established. The denial supplies no explanation adopting the candidate's legal account.

## Leakage and scope

The harness log identifies forward mode. Prediction and call timestamps precede resolution; no query or rationale reveals an already-decided petition. All 27 calls have unobserved results. I assess their query content rather than treating missing dates or digests as proof that retrieval returned nothing. The candidate reports that its corpus query failed, but the transcript does not independently capture that failure. There is no affirmative outcome-retrieval evidence: `retrieved_outcome_material = false`, influence `not_applicable`, and suspected leakage false, subject to that observation limit.

Only `reasoning.md` supplies the qualitative grade. The forecast document was read for context and is not scored. Quantitative claim scoring remains with the harness. No semantic grading or vote accuracy is applicable at cert stage; the denial's silent vote record is not a zero vote score. No independent big-case assessment is supplied.
