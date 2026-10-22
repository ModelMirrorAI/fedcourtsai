# claude-baseline: P(grant) 0.63, predicted `granted`. Outcome: denied.

**Correct:** 0. **Brier:** 0.3969.

**Cell.** This is an **interim** cell: the Solicitor General's application (26A416) to stay a classwide injunction against the BOP gender-dysphoria policy, forecast at the response-filed moment. The Court **denied** the application on 2026-10-21 (`actual_granted` 0, standard basis). The outcome's interim signals: a response was requested, the application was referred to the Court, and two amicus briefs were filed.

**Baseline.** On an interim cell the segment base rate and Brier skill score belong to the harness: `stamp-cell` pools the substantive interim grant rate over application-Terms strictly before 2026 from the committed statpack. I wrote neither, and I quote no hand-pooled rate beside the stamped one. One point for the reader: the committed statpack's interim table has been refreshed since this prediction ran. Terms 2023 and 2024 are now fully parsed, where the prediction-time pack showed 2024 only partly parsed. So the pool a candidate quoted (31/301) may differ from the stamped rate. That is a pack revision, not an error by the candidate.

**Votes and claims.** Interim votes are never scored, so I wrote no `vote_accuracy`. `claim_scores` (interim-v1) is computed by the harness. The cell declares no semantic set, so I wrote no semantic grades.

**Leakage.** The candidate's retrieval log records mode `forward`. The prediction was made on 2026-10-09, and the event resolved on 2026-10-21, so no disposition existed when the prediction was made. I checked the log for this application's disposition surfacing early and found none. Graded `not_applicable`, with `leakage_suspected` false.

**Reasoning quality: 0.62.** This is the strongest analysis of the three. It anchored correctly on the interim baseline, then argued explicitly for moving above it: an SG applicant, the administration's emergency-docket record, and the Shilling and Orr priors. It also read the respondents' opposition in full. Its "why not higher" section names the considerations most consistent with the denial that followed:
- a conventional State Farm record gap that both courts below found;
- the government's delay, including never appealing the 2025 injunction and claiming no irreparable harm below;
- a concrete harm asymmetry for a class receiving ongoing care;
- the 90-day PLRA lapse, which raises a mootness question.

It also split its probability across the outcomes (denial about 0.25, partial about 0.08), and it was candid about the weaknesses of its own anchor: a small tracker denominator and mixed partial/full coding. Where it fell short: it weighted the government-applicant tracker rate (around 0.6 to 0.7 on full grants) above the case-specific defects it had itself identified, so the analysis was better than the number. It was well-reasoned but still miscalibrated toward a grant.
