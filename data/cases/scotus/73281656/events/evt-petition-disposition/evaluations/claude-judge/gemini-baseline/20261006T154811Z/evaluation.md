# Evaluation of gemini-baseline — Lindsey v. South Carolina, No. 25-1176, petition disposition

## Outcome and scores

The event is cert-stage (`kind: petition`, `stage: cert`). The petition was distributed once, for the Conference of September 28, 2026, and **denied on October 5, 2026** with no noted dissent (`actual_granted = 0`, `noted_dissent_from_denial = false`).

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.06 − 0)² = **0.0036**, the best of the three.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`; the statpack table heading names sal-v4, so the versions match. I pooled the bracketed `reached` figures for `baseline` resolved-weighted over OT2017–OT2024, every rendered Term strictly before Term 2025 (caption: 10 of 10 Terms rendered, so no window divergence to flag): 592.9 / 11,580 = 5.12%.
- `brier_skill_score` = 1 − 0.0036 / 0.0512² = **−0.37**. Still negative, since any probability above the 5.1% baseline loses to it on a denial, but the closest to zero of the three.
- `vote_accuracy`, `judgment_correct`: omitted/null, cert stage. No `semantic_grades`: cert cell, no semantic set declared, `record/opinion/` absent as expected.

The forecast document and the `claims` block are not scored here; the harness computes `claim_scores`.

## Reasoning quality: 0.45

The number was closest to the outcome, but `reasoning_quality` grades the soundness of the analysis, and this rationale is thin. It is two paragraphs.

What holds up:

- The anchor is in the right place ("~5-6%" reached rate for a once-distributed baseline-band paid petition) and the candidate correctly kept the probability near it rather than letting the capital marking drive it up. Staying close to the base rate absent strong signals is the right default, and the candidate said so explicitly.
- The reading of Question 2 is broadly right in direction: verbatim adoption of a proposed order is disfavored but has not been held a per se due-process violation, and cert on that question alone is unlikely.
- The CVSG point (state criminal matter, no federal interest) is correct.

What is missing:

- **No engagement with the actual record.** The retrieval log shows the candidate read `questions-presented.txt` but neither `petition.txt` nor `brief-in-opposition.txt`, both of which were provisioned. As a result the rationale never mentions the BIO's preservation objection, the lower court's "in conjunction" and totality language, the 3-2 split below, the state supreme court's prior remand on the drafting errors, or Jefferson v. Upton. Those are the facts that decide whether this is a vehicle, and they are what explain the denial. The rationale's reasons for a low probability (baseline band, no amicus) are proxies that happened to point the right way, not an analysis of the case.
- **The anchor is approximate rather than computed**, and the base-rate reasoning is one sentence. There is no statement of which Terms were pooled or on what n.
- The "known circuit split on cumulative error" is asserted without naming a single court on either side.
- The forecast document (not scored) speculates that "the lower court's decision rests on independent state grounds", which nothing in the record suggests and which the candidate did not check; I note it only because it shows the rationale was not built from the documents.

A forecast that is right for underdeveloped reasons gets credit for the correct instinct about the anchor and for avoiding the capital-case overreaction, and loses most of the rest.

## Leakage: forward, not applicable

`retrieval_log.json` records `mode: forward`, 25 calls, `result_capture_coverage` 0.0: every marker-carrying call is `unobserved`, which is this engine's standing telemetry shape, not a defect, so every call is graded on its query. Two CourtListener docket searches name this case's own docket number, 25-1176. The prediction was created 2026-09-16, when the petition was pending for the 9/28 conference and nineteen days from its 2026-10-05 denial, so no result those searches could have returned carried a disposition that did not yet exist; the candidate's own `retrieval.md` reports no matching docket found. No other call targets this case, and the reasoning treats it as pending. I did not credit the unobserved rows as having returned nothing; the grade rests on the dates. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case

My independent read, formed before looking at the candidate's score, is 0.30 (see `big_case.notes`). The candidate's 0.40 is in the same neighborhood; its rationale (capital case, circuit split, likely poor vehicle) matches my reading in substance. No agreement number is computed.
