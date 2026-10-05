# Evaluation of claude-baseline — scotus/73358839, evt-petition-disposition

## Outcome and scores

Cert-stage cell. The petition for certiorari before judgment (No. 25-1290, Texas Top Cop Shop v. Blanche) was **denied** on 2026-10-05 after the 2026-09-28 conference, with no noted dissent or statement. `actual_disposition = denied`, `actual_granted = 0`.

- `correct = 1`: predicted `denied`, outcome `denied`.
- `brier_score = (0.08 - 0)^2 = 0.0064`.
- `segment_base_rate = 0.172379`, basis `risk_set`. The prediction froze `band = elevated` under `salience_version = sal-v4`, matching the statpack table's heading, so the bracketed `reached` figures apply, pooled resolved-weighted over the rendered Terms strictly before the docket Term (OT2017–OT2024, n = 2,810, ≈ 484.39 grant-equivalents). The caption renders 10 of 10 Terms, so the rendered window is the whole pack and no lookback divergence needs flagging.
- `brier_skill_score = 1 - 0.0064 / 0.172379^2 = 0.7846`.
- `vote_accuracy` omitted (cert stage). `judgment_correct` null. No `semantic_grades` block on a cert cell. `claim_scores` is the harness's.

## Reasoning quality: 0.88

The strongest rationale of the three. It read the record correctly, went and found the two facts outside the record that mattered most, and built the number from an explicit, checkable decomposition.

What earns the mark:

- **Correct anchor, correctly pooled**, with the same eight-Term reached-elevated figure (about 17%) I used, and an honest cross-check against the relist cut that explains why bucket 0, not bucket 2, is the right comparison given the pre-consideration reschedule.
- **It found the dispositive external facts.** FinCEN's August 2026 final rule exempting all domestic entities, and the Solicitor General's opposition in the companion (25-1201) urging denial on that ground. Both were public before the prediction date, both bear directly on whether the Court would reach out on a cert-before-judgment petition, and neither was in the provisioned record. The rationale correctly observed that the rule also removed the urgency argument that was the petition's main Rule 11 hook.
- **Explicit decomposition.** P(grant here) ≈ P(grant in companion) × P(the Court also takes this tag-along), about 0.15 × 0.5, plus a sliver for an independent grant. That is the right structure for a petition whose own vehicle section asks for a grant only alongside NSBU, and it makes the number auditable.
- **Read the petition's own concessions**: abeyance below, the injunction stayed since January 2025, the conditional framing of the ask.
- **A candid "where to discount me" section** that names the trade-press reliance, the judgment call driving the number, and the frozen distribution count overstating true relists.

Where it loses a little:

- It characterizes a Justice as "on record wanting the Court to resolve the CTA's validity definitively." The January 2025 separate writing in this litigation that the rationale is pointing to favored taking the case to settle the scope of universal injunctive relief, not the Act's constitutionality. The inference that a Justice had shown appetite for review of this case is fair; the stated subject of that appetite is not quite right. The error is small and does not drive the headline number.
- It relied on summaries of the companion briefs rather than the briefs themselves, which it disclosed.
- Its 30% on a separate writing respecting denial reads as high given the posture, though I do not score claims and only note it as a place the stakes read may have leaked into a hazard estimate.

## Leakage

Mode `forward`, full result capture. External retrieval: five CourtListener MCP calls (companion docket 25-1201, the Fifth Circuit appeal 24-40792, and an entries query that returned nothing), two web searches (the companion's opposition brief; the FinCEN final rule), and four web fetches (the OSG brief page, two trade-press articles dated July and after August 21, and the companion's public docket page listing entries through September 9, 2026). Every legible document date (2024-12-09, 2026-04-21, entries to 2026-09-09) precedes the 2026-09-28 conference and the 2026-10-05 denial, and the candidate's retrieval note states that nothing surfaced a disposition of this petition or the companion. This is legitimate forward signal about a companion case and a regulatory development, not outcome material about this case. One shell call also read this predictor's own earlier prediction from a prior run under its identity-redacted path; that is its own output, not the docket's. No `data/qp-topics/` read. The prediction's snapshot (2026-09-18) shows the petition pending, so the case was open when predicted. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The candidate's `flags.json` is not staged, so this rests on the log and the prose.

## Big case

My independent read is 0.55 (see the JSON notes). The staged `prediction.json` exposes the candidate's `big_case_score`, so I had seen it before writing my own; I formed the read from the case and the outcome, but note the exposure.
