# Evaluation: claude-baseline — Foley v. Orange County, No. 25-1308 (evt-petition-disposition)

## Outcome and scores

The petition was **denied** on the October 5, 2026 order list after a single distribution (conference of September 28, 2026), with no noted dissent. Cert stage, forward mode.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band" heading names sal-v4, so the bracketed *reached* figures apply. Pooled resolved-weighted over the rendered Terms strictly before OT2025 (OT2017 through OT2024, n = 11,580): 0.0512. The caption renders 10 of 10 Terms, so the rendered window is the pack's full window and no divergence flag is needed.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² ≈ 0.9905.
- No `vote_accuracy` (cert stage; never scored). No semantic block (no semantic set is declared on a cert event).

## Reasoning quality: 0.86

The strongest of the three rationales, and the one that most fully explains *why* this petition sits at the bottom of the baseline band rather than merely asserting it.

What it got right:

- **The claimed split is dissolved correctly.** The rationale observes that the "every other circuit" authorities hold Rule 60(b)(4) relief mandatory *once a judgment is void*, which Espinosa already says, and that the Eleventh Circuit did not hold otherwise. It held that the earlier panel had necessarily decided the point, so law of the case barred relitigation. That is the right reading of the petition's own account and is the core reason the QP was not cert-worthy.
- **The voidness theory is tested against Espinosa.** Reading Reynolds v. Stockton as making any judgment "outside the pleadings" void is measured against Espinosa's confinement of voidness to jurisdictional and notice/opportunity defects. The conclusion that mis-characterizing a property interest is at most merits error is sound.
- **Vehicle features are enumerated and weighed**: pro se, unreported affirmance, Rule 38 sanctions below, both respondents waived, no amicus, a prior cert denial on the same dispute in 2024. Each is a real depressant of the grant hazard.
- **Base-rate hygiene.** The anchor is the correct table, the correct bracketed figure, pooled over the correct Terms (about 5.1%, n ≈ 11,600), and the rationale explicitly notes that the relist-0 bucket is a terminal-state figure that understates the forward hazard rather than stacking it as an adjustment.
- **Honest limits**: it flags that its account of the decision below is the petitioner's own, that the CourtListener searches found nothing, and that the corpus queries returned non-comparable stay applications.

What holds it short of higher:

- The final number (0.005) is a very deep discount from the 5.1% anchor, and the rationale's justification for the magnitude is qualitative ("pro se paid petitions grant at a small fraction of the counseled rate") rather than tied to any figure in the pack. The direction and the ordering are well supported; the precise depth is asserted. The outcome vindicates the direction, but a denial at first conference is also consistent with 0.02, so the realized result cannot discriminate the depth.
- A minor over-reach: "Respondents' waivers signal they see no risk" is a fair inference, but a waiver is the default for a county facing a pro se petition and carries less information than stated.

## Leakage: forward, not applicable, `leakage_suspected` false

Mode `forward` in the log. The prediction was created September 17, 2026 against a September 16 snapshot; the petition was still awaiting its September 28 conference and was denied October 5. The log has full result capture (coverage 1.0). The only external calls were two corpus queries over granted and denied 2020s dockets (one retrieved_doc_date of 2026-09-10, a stay application unrelated to this case) and two CourtListener opinion searches for the Eleventh Circuit decision below, both returning zero results. Nothing targeted or surfaced this petition's disposition, and the reasoning treats the case as pending throughout. No `data/qp-topics/` read. `retrieved_outcome_material` = false. The case was not mis-provisioned: it was genuinely open at prediction time.

## Big case: 0.05 (independent read)

Formed before reading the candidate's score. A pro se Rule 60(b)(4) / law-of-the-case petition arising from an unreported Eleventh Circuit affirmance of a local code-enforcement dispute, with waivers from every respondent, no call for a response, and denial at first conference. Stakes confined to the parties.

## Not graded here

`predicted_reasoning.md` and the `claims` block were read for context only; the harness scores the claims in code and the forecast document is not graded on any stage.
