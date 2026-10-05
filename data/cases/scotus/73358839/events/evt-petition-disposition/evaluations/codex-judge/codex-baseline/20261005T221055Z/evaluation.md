# Evaluation: codex-baseline

Case: `scotus/73358839`; event: `evt-petition-disposition`; evaluator: `codex-judge`; evaluation run: `20261005T221055Z`. Scored blinded prediction run: `20260918T195102Z`.

## Observed outcome and numerical scores

The provisioned `outcome.json` records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The provisioned snapshot has an October 5 entry reading "Petition DENIED." The candidate predicted **denied** with grant probability **0.08**. Exact-label correctness is **1**; Brier loss is `(0.08 - 0)^2 = 0.0064`. Skill against the shared prior-Term baseline is `1 - 0.0064 / (0.172379359430605 - 0)^2 = 0.784617978419589`. This is a per-cell comparison, not an aggregate performance claim.

## Baseline and scoring scope

The scored prediction freezes `context.term = 2025`, `context.band = elevated`, and `context.salience_version = sal-v4`. The committed `metrics/statpack.md` heading matches that version. I use its bracketed **reached elevated** risk-set rates, never the evaluator's terminal context or the leading terminal rates. The eligible displayed rows are OT2017–OT2024; OT2025 and OT2026 are excluded. Their published rates and weighted resolved denominators are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336, respectively. Thus the pooled baseline is 484.386 / 2,810 = **0.172379359430605**, with `base_rate_basis = risk_set`. The numerator is a grant-equivalent reconstructed from rounded published rates, not an exact grant count. The caption renders 10 of 10 Terms, so there is no omitted-window divergence to flag.

These are calculations from the committed, denial-reweighted live/historical-slice statpack supplied in this checkout, not fresh corpus measurements. I did not query or refresh the corpus and do not assert a newest-pull vintage. Case ground truth is the provisioned October 5, 2026 outcome and snapshot.

This is a **cert** event. No vote accuracy, judgment score, or semantic grades are supplied. Quantitative claims are left for the harness; the court-action forecast document was read only for context and leakage review, not scored. The quality judgment below is confined to `reasoning.md`, independently of exact-match and Brier performance. The short denial supplies no Court explanation, so it does not establish that any hypothesized reason actually motivated the Court.

## Reasoning quality: 0.90

The rationale distinguishes the petition's substantive importance from the reasons to grant this particular cert-before-judgment vehicle. It grounds the exceptional-review posture in the petition's jurisdiction section, distinguishes a district-court/appellate disagreement from an established split between appellate courts, and identifies the companion vehicle, response waiver, and regulatory complication. It correctly distinguishes two distribution entries from two actual conference considerations: the June distribution was rescheduled before the scheduled conference. Its prior-Term risk-set calculation is reproducible and agrees with the evaluator's baseline.

The petition's procedural account supports the discussion of the interim domestic-company exemption and the abeyance pending rulemaking. The candidate expressly avoids assuming mootness or claiming that the prior emergency stay decided the cert petition. It identifies the one-sided advocacy and absence of a substantive opposition, and does not invent a current companion status. The principal limitation is the judgmental reduction from roughly 17.24% to 8%, without an independently calibrated comparable-vehicle sample; regulatory and companion developments remained unverified. Those disclosed limits justify a high but not perfect analysis score. The observed denial supports the forecast label, not a finding that the Court adopted the proposed rationale.

## Leakage assessment

`mode = forward`; `retrieved_outcome_material = false`; `influenced_prediction = not_applicable`; `leakage_suspected = false`.

The captured transcript dates the work to September 18, before this petition's October 5 disposition. Of 28 calls, 26 have captured results (coverage 0.9285714285714286). The two unobserved web calls concern Rule 11 and the Court's Rules PDF, not this case's disposition. Although the retrieval note calls them unsuccessful, their markers do not establish empty or failed results; I assess their general-law query scope instead. The remaining reads and prose contain no outcome-revealing material about this petition. No forward mis-provisioning is apparent.
