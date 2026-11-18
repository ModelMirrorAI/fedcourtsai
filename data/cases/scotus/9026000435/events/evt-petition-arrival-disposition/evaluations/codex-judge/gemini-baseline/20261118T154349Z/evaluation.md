# Evaluation: gemini-baseline

This is a cert-stage arrival evaluation. Ground truth is `outcome.json`: denied on November 16, 2026, `actual_granted = 0`, no CVSG and no noted dissent from denial. The staged November 16 snapshot records an October 23 government waiver, an October 28 distribution for the November 13 conference, and denial on November 16. It records one distribution and no request for a response or further conference. No Supreme Court opinion or separate-writing text is staged. The bare denial supplies no explanation of the Court's reasons.

Base-rate use was checked against the historical sal-v4 statpack reconstructed by `uv run fedcourts statpack-at`, build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5` (digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e`), rather than the current sal-v8 build. There is no alternative build reported. The private-petitioner baseline risk set and strictly prior OT2017–OT2025 rows are appropriate; the historical table supports the candidate's approximate starting calculation. The federal respondent does not change the petitioner's caption class. The stamped segment base rate and skill are the harness's; no independently pooled evaluation anchor is reported here.

Votes are unscored on cert, and no semantic set applies. Quantitative claims are left entirely to the harness.

The denial label is correct: `correct = 1`. P(grant) was 0.12, so the binary Brier score is `(0.12 - 0)^2 = 0.0144`.

`reasoning_quality = 0.47` grades `reasoning.md` alone. The rationale correctly identifies the private-petitioner baseline population, uses strictly prior Terms, treats the NLRB's presence as reducing the need for a CVSG, and retains denial as the likely outcome. It acknowledges that a respondent might identify factual-review or vehicle problems.

The substantial upward adjustment rests largely on the questions presented alleging defiance of Loper Bright and a circuit split. The rationale does not examine the supplied petition's appendix, and the captured query list contains no petition-text read. The attached order supplies precisely the distinction left hypothetical: it recites de novo legal review (App. 3a) and resolves supervisory status through concrete evidentiary deficiencies (6a–8a). The petition itself describes the Second Circuit's later Siren Retail decision as adopting independent review (petition 13–14). Those materials needed assessment before labeling this an attractive enforcement vehicle. The historical statpack's terminal distribution buckets also do not establish the prospective relist hazard invoked in the prose. This is a limitation of the rationale's evidence and inference, not a manual score of any structured claim.

The correct denial call does not cure the thin examination of the available legal record. No inference about the Court's actual reasons can be drawn from its unexplained denial.

## Predicted reasoning

`predicted_reasoning_quality = 0.40`. Denial and no CVSG were correct, but the document's leading expectation of a relist failed: there was one initial conference distribution and no repeat conference. Its assertion that the government would file a brief also failed; the government waived a response. The suggestion of a possible dissent was hedged, and no noted dissent appears, so that possibility earns no specificity credit. The first-question/plenary-review forecast was expressly conditional on a grant that never occurred and receives neither credit nor penalty. The grade reflects correct direction mixed with a failed central procedural call; it does not treat unobservable internal debate as an established fact.

## Leakage

The log records forward mode and October 1 calls, before the November 16 denial. Every result is unobserved (coverage 0.0); this is capture shape, not evidence of failed calls or missing results. The visible queries target instructions, schemas, the arrival snapshot, questions presented and statpack, followed by output/validation calls. No visible query or prose supplies this case's disposition. Assessment rests on call intent and prose, not presumed empty results. The forward default applies: `influenced_prediction = not_applicable`, `retrieved_outcome_material = false`, and `leakage_suspected = false`. The evaluator's later, fully resolved snapshot is evidence for grading and is not treated as the candidate's original information set.
