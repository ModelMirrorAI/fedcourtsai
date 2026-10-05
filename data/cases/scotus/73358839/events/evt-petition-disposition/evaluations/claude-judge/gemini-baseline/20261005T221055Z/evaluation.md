# Evaluation of gemini-baseline — scotus/73358839, evt-petition-disposition

## Outcome and scores

Cert-stage cell. The petition for certiorari before judgment (No. 25-1290, Texas Top Cop Shop v. Blanche) was **denied** on 2026-10-05 after the 2026-09-28 conference, with no noted dissent or statement. `actual_disposition = denied`, `actual_granted = 0`.

- `correct = 1`: predicted `denied`, outcome `denied`.
- `brier_score = (0.15 - 0)^2 = 0.0225`.
- `segment_base_rate = 0.172379`, basis `risk_set`. The prediction froze `band = elevated` under `salience_version = sal-v4`, matching the statpack table's heading, so the bracketed `reached` figures apply, pooled resolved-weighted over the rendered Terms strictly before the docket Term (OT2017–OT2024, n = 2,810, ≈ 484.39 grant-equivalents). The caption renders 10 of 10 Terms, so the rendered window is the whole pack and no lookback divergence needs flagging.
- `brier_skill_score = 1 - 0.0225 / 0.172379^2 = 0.2428`. Beats the band baseline, but by much less than the other candidates.
- `vote_accuracy` omitted (cert stage). `judgment_correct` null. No `semantic_grades` block on a cert cell. `claim_scores` is the harness's.

## Reasoning quality: 0.50

The rationale lands on the right disposition for broadly the right reason, but the analysis is thin and carries two substantive errors.

What it got right:

- It identified cert before judgment as the central obstacle and correctly noted that the Court prefers a final appellate judgment, and that a parallel case offered a more conventional vehicle.
- It read the government's response waiver correctly as a signal of low respondent engagement, and reasoned correctly that no CVSG could issue because the Solicitor General is already respondent.
- It noticed that one of the two distributions was a reschedule.

What pulls the mark down:

- **Wrong base-rate row.** It anchored on "13.5% (reached)", which is the OT2025 row, the case's own Term. The contract calls for Terms strictly before the case's; pooled, that is about 17%. In a forward cell this is not leakage, but it is the wrong number under the pre-registered rule, and it is read off a single still-open Term rather than a pooled window.
- **Misdescribed the split.** It says a circuit split is "actively developing" because the Eleventh Circuit "split with the district court in this case." A court of appeals disagreeing with a district court is not a circuit split, and the Fifth Circuit has not ruled (the appeal is in abeyance). Treating this as a split overstates the grant case; the other candidates read the same record correctly.
- **The adjustment does not follow from the analysis.** The rationale lists strong reasons for denial (cert before judgment "rarely granted", waiver, poor vehicle), then says it is "adjusting the probability near the baseline" and lands at 15%, above the band rate it cited. Reasons that point firmly down should move the number down, or the rationale should say why they do not.
- **No engagement with the record's own complications.** The petition itself discloses the abeyance, the stayed injunction, the interim domestic-company exemption, and frames its ask as conditional on a grant in NSBU. None of this appears. The relist probability (0.45) is asserted as "moderate chance" without a mechanism.

The write-up is honest and short, and its retrieval note says exactly what it used. But as legal analysis it is a sketch, and two of its factual claims are off.

## Leakage

Mode `forward`. The log shows 22 calls, every one a local read of the prompt, the provisioned record, the statpack, or the schema, or a file write of the outputs. No web, MCP, or corpus call at all. Every marker-carrying call is `unobserved` (`result_capture_coverage = 0.0`), which is this engine's standing telemetry shape, not a defect; graded on their queries, none reaches outside the checkout and none touches `data/qp-topics/`. The prediction's snapshot (2026-09-18) shows the petition pending, so the case was open when predicted. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The candidate's `flags.json` is not staged, so this rests on the log and the reasoning.

## Big case

My independent read is 0.55 (see the JSON notes). The staged `prediction.json` exposes the candidate's `big_case_score`, so I had seen it before writing my own; I formed the read from the case and the outcome, but note the exposure.
