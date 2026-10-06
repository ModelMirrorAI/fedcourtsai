# Evaluation — codex-baseline, Winnemucca Indian Colony v. United States (scotus/73281654, evt-petition-disposition)

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on 2026-10-05 after the 2026-09-28 conference, with no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 2`).

- `predicted_disposition: denied` → **correct = 1**.
- `probability: 0.06` → **brier_score = 0.0036**.
- **segment_base_rate = 0.1722** on the `risk_set` basis: the prediction froze `band: elevated` under `salience_version: sal-v4`, the statpack's table heading names sal-v4, so the bracketed `reached` figures apply. Pooled resolved-weighted over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the caption shows 10 of 10 Terms, so the rendered window is the whole pack and matches the configured ten-Term lookback over the rows that exist): weighted grants 484.0 over n = 2810, giving 0.17224 from the statpack JSON's exact `prefix_est_grant_rate` / `prefix_weighted_resolved` fields. Baseline Brier (0.1722 − 0)² = 0.02967.
- **brier_skill_score = 1 − 0.0036 / 0.02967 = 0.8787.**
- `vote_accuracy`, `judgment_correct`: not applicable on a cert cell; omitted / null. `claim_scores` and `process_version` are the harness's.

## Reasoning quality: 0.82

What drove the score, from `reasoning.md` only:

- **Anchor handled exactly as the contract asks.** The candidate pooled the elevated band's bracketed `reached` figures over Terms 2017–2024 (its 17.24%, n = 2810 reconstruction matches the exact 17.22%), excluded the case's own Term, and correctly refused to use the terminal relist and CVSG buckets as hazard rates.
- **Correct reading of the docket shape.** It recognised that the second distribution followed a call for a response that pulled the petition off the May 28 conference, so the "relist" signal was weaker than a post-conference relist — the single most important structural fact in this record, and the reason the elevated band overstated the petition's position.
- **Accurate on the holdings below.** It correctly separated the three CFC grounds (source of duty, §1500, §2501) from what the Federal Circuit actually affirmed on, noting that the court of appeals did not reach §1500 for the water claim. That matches the brief in opposition (BIO 10–11).
- **Substantive engagement with both briefs.** It identified the existing-water vs. new-water distinction as the petition's strongest point, weighed the government's textual answer on 25 C.F.R. 152.22 and Ute, and read the retrieved Navajo Nation passages for the specific-duty requirement rather than as a slogan.
- **Epistemic hygiene.** It kept attributed advocacy separate from established fact, disclosed that the reply was not provisioned, and stated the pack's vintage honestly.

Where it loses points: the write-up is long for the decision it supports and the Navajo Nation retrieval added little beyond what both briefs already quoted; the final 0.06 is a judgmental step from the anchor with no stated intermediate (the candidate says as much), and the 0.25 further-distribution figure sits a little high for a petition reaching its first real conference fully briefed. None of these is an error; the number was well inside the band of a sound analysis, and the denial bore the analysis out.

## Leakage

Forward cell: `retrieval_log.json` records `mode: forward`, coverage 0.94. I scanned the log and the prose for this case's own disposition surfacing as already decided and found nothing: no `retrieved_doc_date` on or after 2026-10-05, no query for this docket's status, external calls confined to a 2023 precedent (two unobserved web calls for the Navajo Nation PDF, three captured CourtListener calls), and the reasoning states the outcome was unknown. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was genuinely pending when the prediction was made (created 2026-09-18, denied 2026-10-05), so the forward provisioning was correct.

## Big case

My independent read is 0.18 — see `big_case.notes` in `evaluation.json`. A narrow, fact-bound damages vehicle in a live doctrinal area, denied without a writing.
