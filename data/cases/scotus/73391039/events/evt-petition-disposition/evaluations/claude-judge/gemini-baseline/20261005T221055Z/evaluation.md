# Evaluation: gemini-baseline — Foley v. Orange County, No. 25-1308 (evt-petition-disposition)

## Outcome and scores

The petition was **denied** on the October 5, 2026 order list after a single distribution (conference of September 28, 2026), with no noted dissent. Cert stage, forward mode.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.01 − 0)² = 0.0001.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack table's heading, so the bracketed *reached* figures apply, pooled resolved-weighted over OT2017 through OT2024 (n = 11,580): 0.0512. The caption renders 10 of 10 Terms, so no window-divergence flag.
- `brier_skill_score` = 1 − 0.0001 / 0.0512² ≈ 0.9619.
- No `vote_accuracy` (cert stage). No semantic block (cert event declares none).

## Reasoning quality: 0.58

A short, correct, but thin rationale. Everything it says is sound; what it does not say is most of the case.

What it got right:

- **Correct anchor and correct direction.** It names the baseline band under sal-v4, pools the prior-Term reached rate at roughly 5%, and adjusts downward from there rather than from a terminal bucket.
- **The waiver inference is legitimate**, and the observation that the Court does not grant without first calling for a response is accurate practice: a petition with waivers on file and no response request is, mechanically, not on a grant path at this conference.
- **Characterizing the QP as fact-bound** is the right conclusion.

What limits it:

- **The petition itself was not engaged.** The log shows reads of the snapshot, the questions presented, and the manifest, but not `petition.txt`. The rationale therefore never tests the petition's claimed circuit split (which dissolves on inspection because the cited circuits agree with the Eleventh Circuit on the mandatory-relief point and differ only on whether the issue was already decided), never mentions Espinosa's limits on voidness, and never notes the features that most distinguish this petition from the band average: pro se filing, an unreported affirmance, Rule 38 sanctions below, and a prior cert denial on the same dispute. The conclusion "fact-bound" is asserted from the QP's surface rather than shown.
- **The downward adjustment rests on a single signal.** The waiver is doing almost all the work. That signal was correct here, but a rationale that would have produced the same number for any waived baseline petition is not discriminating among them.
- No stated uncertainty, no account of what would move the number, and no engagement with the one route (a summary vacatur of the sanctions award) by which a grant was conceivable.

The number itself (0.01) is reasonable and within the range the evidence supports; the score reflects the shallowness of the analysis behind it, not the forecast.

## Leakage: forward, not applicable, `leakage_suspected` false

Mode `forward`. Prediction created September 17, 2026 against the September 16 snapshot, before the September 28 conference and the October 5 denial. The log's `result_capture_coverage` is 0.0, every call `unobserved`, which is this engine's standing telemetry shape and not a defect; each call is graded on its query. All queries are local reads of the provisioned record, `event.yaml`, `context.json`, and `metrics/statpack.md`, plus the candidate's own output writes. No web search, no CourtListener call, no query naming this docket number or disposition, no `data/qp-topics/` read. The candidate's `retrieval.md` states no retrieval beyond the provisioned inputs, consistent with the log. `retrieved_outcome_material` = false. The case was genuinely open at prediction time.

## Big case: 0.05 (independent read)

Formed before reading the candidate's score. A pro se Rule 60(b)(4) / law-of-the-case petition from an unreported Eleventh Circuit affirmance of a local code-enforcement dispute; respondents waived, no response requested, denied at first conference. Stakes confined to the parties.

## Not graded here

`predicted_reasoning.md` and the `claims` block were read for context only; the harness scores the claims in code and the forecast document is not graded on any stage.
