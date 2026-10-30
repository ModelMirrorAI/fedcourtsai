# Evaluation: gemini-baseline

## Outcome and mechanical scores

This is a cert-stage distribution cell. The authoritative outcome is `dismissed`, with `actual_granted = 0`, resolved October 26, 2026. The provisioned docket records a joint Rule 46 dismissal stipulation filed October 23 and dismissal October 26. It does not record denial of certiorari or adjudication of the choice-of-law question.

The candidate predicted `denied`, so exact-label correctness is **0**. Its binary non-grant call was directionally right but does not earn exact-label credit for a dismissal. With grant probability 0.25, the Brier score is `(0.25 - 0)^2 = 0.0625`.

The prediction froze the `baseline` band under `sal-v4`, Term 2026. The harness supplies the stamped segment base rate and associated skill; neither is supplied or independently pooled here. Cert votes are not scored. No semantic set is declared on this stage. Mechanical claim scoring is left entirely to the harness, and `predicted_reasoning.md` is read for context only, not graded.

## Reasoning quality: 0.50

The rationale correctly treats a response requested after waiver as a signal of attention rather than a grant, identifies the federal-versus-state equitable-estoppel question, and recognizes that a substantial claimed circuit conflict can still end without review. Keeping the grant probability below one-half is coherent with that account.

However, the analysis largely adopts the petitioners' split characterization without testing its scope or discussing the unpublished summary affirmance, the requested hold for related litigation, or the foreign-party and separate-contract vehicle complications visible in the provisioned petition. The asserted strong vehicle is insufficiently supported. The jump to 25% is judgmental without a developed explanation of its size. The rationale's roughly 1% anchor does not distinguish terminal-baseline from reached-band populations, an important distinction for a frozen-band prediction. Its near-guarantee of redistribution overlooks withdrawal or settlement before another distribution; the observed dismissal illustrates that omitted branch without proving it was foreseeable at the time.

The candidate reports that the petition and manifest were unavailable. Its captured query text instead shows an attempted read of `record/documents.json`, followed by a listing of `record/`, and no read of `record/documents/petition.txt`. The evaluation record does contain those documents in `record/documents/`; this does not establish what was present in the original prediction workspace. I treat this as a limitation on the candidate's evidentiary basis, not proof of missing provisioning or fabrication. The quality score reflects the rationale's shallow vehicle analysis, not a separate grade of the forecast document or structured claims, and not simply the incorrect outcome label. Rule 46 dismissal neither confirms nor refutes the asserted legal split.

## Leakage and significance

The log identifies a forward run, and the prediction was created October 6, before either the dismissal stipulation or disposition. The 32 calls all have `result_capture: unobserved`, so capture coverage is 0.0. Null result dates and digests are not evidence that searches returned nothing. The visible queries seek the caption, docket, and underlying arbitration dispute; neither the rationale nor retrieval note describes a disposition. No outcome exposure is evidenced, so `retrieved_outcome_material` is false, influence is `not_applicable`, and leakage is not suspected. This is a qualified assessment of available evidence, not a claim to have inspected uncaptured results.

My independent significance assessment is **0.35**: a consequential but technical international-arbitration question, presented in a derivative insurance vehicle. The record shows procedural termination, not a new rule. No external case retrieval or fresh corpus-state claim was needed.
