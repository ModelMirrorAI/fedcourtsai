# Evaluation: gemini-baseline — Zook v. Fuqua, No. 25-1108 (scotus/73281401), evt-petition-disposition

## Outcome and headline scores

The petition was **denied** on the 2026-10-05 order list after the 2026-09-28 long conference, with no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 2, `noted_dissent_from_denial` false). Cert-stage cell (`event.yaml` stage `cert`).

- `correct` = 1: `predicted_disposition` denied matches the outcome label exactly.
- `brier_score` = (0.17 − 0)² = **0.0289**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The frozen context carries band `elevated` under `sal-v4`, matching the statpack's "Segment base rate by salience band (sal-v4)" heading, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017–OT2024; the caption renders 10 of 10 Terms, so no window divergence): 17.9% (n=336), 17.5% (354), 19.0% (300), 20.5% (342), 16.1% (397), 13.8% (334), 15.9% (347), 17.5% (400) → 484.4 / 2810 = 0.1724. Baseline Brier 0.0297.
- `brier_skill_score` = 1 − 0.0289 / 0.0297 = **0.0276**. Essentially zero: the forecast parrots the band rate, and the skill it shows is the rounding from 17.2% to 17%.
- No `vote_accuracy`, no `semantic_grades`: cert stage. `claim_scores` is the harness's.

## What the prediction got right and wrong

Right: the disposition, the base-rate anchor (correct table, correct figure, correct Term window), the generic shape of the vehicle problem (a fact-bound shooting makes the broader pleading question unattractive), and the expectation of no further relist, which held.

Wrong: the reading of the docket signal. `reasoning.md` says the petition "has already been distributed twice, increasing the likelihood of a grant", and describes "the current relist reflecting the Court's consideration of the split before passing on the messy vehicle." The provisioned snapshot shows a response request on May 15 between the May 5 and July 29 distributions, so the petition had never been considered at conference when the prediction ran; there was no relist and no "consideration of the split" to infer. The statpack itself warns that the stored distribution count is an upper bound on relists for exactly this reason. Both other candidates read the same snapshot correctly. The candidate also made essentially no adjustment (17.2% → 17%) despite naming a vehicle problem, so the stated reasoning and the number do not quite agree.

## Reasoning quality: 0.40

`reasoning.md` is two paragraphs. Its anchor is correct and correctly sourced, which is the main thing it does well. Beyond that the analysis rests on the questions presented alone: the vehicle point is argued from the facts recited in QPs 2 and 3, not from the petition, the brief in opposition, or the opinion below, all three of which were provisioned (the petition and BIO as full text) and which the retrieval log shows the candidate did not open. As a result it misses the decisive argument the BIO makes and the other candidates verified, the Tenth Circuit's alternative holding that the videos would not blatantly contradict the complaint even under the Sixth Circuit rule, and it misses the amended-complaint development. The misreading of the two distributions as a relist is a factual error about the provisioned snapshot that pushed in the wrong direction and should have been visible from the docket entries. The write-up is directionally sensible and ended up correct on the label, but the number is the base rate with a one-point haircut, and the reasoning does not engage the case-specific record it was given. The forecast document and the claims block were not graded and did not enter this number.

## Leakage: forward, not applicable

Mode `forward` per `retrieval_log.json`. The prediction was created 2026-09-17 against the 2026-09-17 snapshot, eighteen days before the denial, so no outcome existed to leak. Checked anyway: 23 logged calls, every one marked `unobserved` (capture coverage 0.0, an engine's standing telemetry shape, not a defect), so each call is graded on its query: reads of AGENTS.md, the prompt, the record's context, snapshot directory, documents directory, event.yaml, questions presented, the statpack table, its own output writes, and `validate`. No web, MCP, or corpus call; no query names anything outside the provisioned cell; no `data/qp-topics/` read. The candidate's `retrieval.md` ("No retrieval beyond the provisioned inputs and the committed statpack") matches. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big-case read: 0.30

Formed from the record and outcome before weighing the candidate's score. A paid Section 1983 petition from county deputies with a recurring procedural question (video at Rule 12(b)(6)) and a claimed circuit split, but no amicus support, non-specialist counsel, a fact-bound shooting, an alternative holding below, and a silent denial. Moderate-low stakes. The candidate's own score is not graded here.
