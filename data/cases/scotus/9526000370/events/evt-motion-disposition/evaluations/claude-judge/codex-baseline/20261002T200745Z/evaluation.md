# Evaluation of codex-baseline — scotus/9526000370 / evt-motion-disposition

**Stage: interim** (a stay application, `event.yaml` stage `interim`). **Outcome:** application denied by Justice Kagan on 2026-10-01, in chambers, without referral; response requested on 2026-09-18; no amicus. `actual_granted` = 0.

## Scores

- **Prediction:** `granted`, P(unqualified grant) = 0.62.
- **`correct` = 0** (`granted` vs `denied`).
- **`brier_score` = (0.62 − 0)² = 0.3844.**
- **`segment_base_rate` / `brier_skill_score`:** not written. On an interim cell both are the harness's: `stamp-cell` pools the statpack interim section's substantive resolved slice over application-Terms strictly before the prediction's own (Term 2026) and clears both where the pool is under the registered floor of 50. From the committed pack the pool should be Terms 2025 (17/226) and 2024 (14/70), 31/296 ≈ 10.5%, which clears the floor; if the stamp comes back null, the cause would be the pack's parse coverage (Terms 2023 and earlier are wholly unparsed), not a missing section. `base_rate_basis` is null structurally — an application freezes no band.
- **`vote_accuracy`:** omitted (not a merits cell). **`semantic_grades`:** none (no semantic set on an interim event). **`claim_scores`:** the harness's.

## Reasoning quality: 0.55

A careful, well-organised and candid rationale whose weighing went wrong.

Strengths:

- **Anchor and provenance.** The pooled rate (31/296 = 0.1047) is computed correctly with the window stated, the 2026 row and the pack-level rate excluded, the coverage caveats spelled out, and the statpack's commit date distinguished from corpus freshness.
- **It read the adverse record.** Unlike a purely applicant-side read, it used the appended district-court and Ninth Circuit orders: intermediate measures tried, fourteen years of failed correction, preventable deaths, and the fact that Judge Forrest's partial dissent favoured only an administrative stay and referral to the merits panel. It cited *Nken* for the primacy of likelihood of success and irreparable injury, located independently.
- **It named its own failure mode.** "The strongest reason it could be wrong is that the Court credits the lower court's necessity findings and sees the appeal as the appropriate place to resolve the factual dispute." That is what happened.

Why the score is middling rather than high:

- **The weighing does not follow from the analysis.** Having identified a fact-bound remedial dispute, an expedited appeal, adverse necessity findings and a demanding stay standard, the document still puts 0.62 on an *unqualified* grant — six times the anchor — on the strength of the remedy's scope and the sovereign applicant. The lift is attributed to "the scope and timing of the remedy", which is an irreparable-harm point, while the likelihood-of-success half of *Nken* it had just cited is left as "a plausible legal route". Certworthiness as a threshold for emergency relief — no split, a novel *CASA* hook the applicant itself says need not be resolved — is not addressed at all.
- **It chose not to look at the live docket.** Forward retrieval was permitted, and the respondents' opposition had been on file for two days. The document acknowledges it "cannot claim a complete adversarial record"; the choice to forecast anyway at 0.62 without it is a judgment call that cost accuracy.
- Referral at 0.87 and amicus at 0.65 were both wrong, in the same direction as the headline: the Court treated this as a routine in-chambers matter, which the analysis never seriously contemplated.

The document is substantially better than a heuristic read — it engages the record, states the standard, and flags its limits — but the number it produces is not the number its own reasoning supports.

## Leakage

Forward mode; `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false. The log (coverage 0.92) shows local reads of the provisioned inputs, the statpack and the application text; two unobserved web-search rows graded on their queries (a *Nken* citation lookup and a supremecourt.gov opinion PDF path — general authorities); and two CourtListener calls on the *Nken* opinion. No live-docket read, no query naming this case, no `data/qp-topics/` read. The prediction predates the 2026-10-01 denial by four days.

## Big case

My own read is 0.5 — see the `big_case.notes` field. The predictor's 0.82 weights the underlying remedial stakes heavily; the Court's in-chambers handling points lower.
