# Evaluation — gemini-baseline, Winnemucca Indian Colony v. United States (scotus/73281654, evt-petition-disposition)

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on 2026-10-05 after the 2026-09-28 conference, with no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 2`).

- `predicted_disposition: denied` → **correct = 1**.
- `probability: 0.01` → **brier_score = 0.0001**.
- **segment_base_rate = 0.1722** on the `risk_set` basis: the prediction froze `band: elevated` under `salience_version: sal-v4`, matching the statpack table's heading, so the bracketed `reached` figures apply. Pooled resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the caption shows 10 of 10 Terms, so the rendered window is the whole pack): weighted grants 484.0 over n = 2810, giving 0.17224 from the statpack JSON's exact per-Term fields. Baseline Brier 0.02967.
- **brier_skill_score = 1 − 0.0001 / 0.02967 = 0.9966.**
- `vote_accuracy`, `judgment_correct`: not applicable on a cert cell. `claim_scores` and `process_version` are the harness's.

## Reasoning quality: 0.45

The candidate reached the right answer with the best Brier of the three, but `reasoning_quality` grades the soundness of the analysis, and this one has a material factual error at its foundation and is thin where the record demanded care.

- **Factual error on the decision below.** The first of the candidate's "three severe vehicle problems" is that the Federal Circuit's decision "is unpublished and non-precedential." Both provisioned briefs say otherwise: the petition's Opinions Below states the decision "is reported at 156 F.4th 1339 (Fed. Cir. 2025)", and the brief in opposition's Opinions Below says the same. A reported F.4th opinion is a precedential one. The candidate reports having read the opinion on CourtListener, which makes the mischaracterisation harder to excuse, and the error is load-bearing: it is offered as a reason for review being unlikely.
- **Conflation of the holdings below.** "The court dismissed the continuing trespass claims under the Section 1500 jurisdictional bar … and dismissed other claims under the six-year statute of limitations" blurs the Court of Federal Claims and the Federal Circuit. On the brief in opposition's account, the Federal Circuit affirmed §1500 dismissal of several *other* claims but expressly did not reach §1500 for the water claim, which it affirmed on the source-of-law ground; §2501 was a CFC holding. The candidate's conclusion — independent procedural obstacles make the water question a poor vehicle — is right, but the reasoning gets there by misdescribing who held what.
- **The anchor is quoted, not used.** "Roughly 13–20% reached grant rate" is read off the table; no pooling, no stated prior-Term window, and no explanation of how 0.01 follows from a ~17% anchor. The response-request redistribution — the fact that makes the elevated band overstate this petition — is not analysed in `reasoning.md` at all (the forecast document mentions it in passing, but that document is unscored).
- **A number more confident than its support.** 0.01 is below the whole-population paid grant rate and well below the band anchor for a petition on which the Court called for a response after a waiver. The denial vindicated the direction, but a petition that drew a CFR is not a 1-in-100 grant on this showing, and nothing in the write-up prices the CFR.

What it got right: no plausible circuit split; the decision below is a faithful application of Arizona v. Navajo Nation; a CVSG is impossible with the United States as respondent; the government's BIO is strong. Those are the correct core points, briefly and correctly stated, and they carry the score to the middle of the range rather than lower.

## Leakage

Forward cell: `retrieval_log.json` records `mode: forward`, `result_capture_coverage` 0.0 — every call is `unobserved`, which is this engine's standing telemetry shape rather than a defect, so each call is graded on its query. The queries are file reads of the provisioned record and statpack; a CourtListener search for "Winnemucca" "United States"; a `read_document` of opinion 11171627 (the Federal Circuit decision below, dated 2025-10-16, which predates the petition); a `search_document` for "Navajo" in that opinion; and two `fedcourts query` calls bounded by `--decided-before 2026-09-17`. None reaches past the event date or seeks this petition's disposition, and the reasoning presupposes a pending petition. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was genuinely pending when predicted (created 2026-09-18, denied 2026-10-05).

## Big case

My independent read is 0.18 — see `big_case.notes` in `evaluation.json`.
