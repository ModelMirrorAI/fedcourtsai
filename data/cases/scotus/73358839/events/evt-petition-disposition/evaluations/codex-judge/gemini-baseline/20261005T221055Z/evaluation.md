# Evaluation: gemini-baseline

Case: `scotus/73358839`; event: `evt-petition-disposition`; evaluator: `codex-judge`; evaluation run: `20261005T221055Z`. Scored blinded prediction run: `20260918T195102Z`.

## Observed outcome and numerical scores

The provisioned `outcome.json` records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The provisioned snapshot has an October 5 entry reading "Petition DENIED." The candidate predicted **denied** with grant probability **0.15**. Exact-label correctness is **1**; Brier loss is `(0.15 - 0)^2 = 0.0225`. Skill against the shared prior-Term baseline is `1 - 0.0225 / (0.172379359430605 - 0)^2 = 0.242797580381366`. This is a per-cell comparison, not an aggregate performance claim.

## Baseline and scoring scope

The scored prediction freezes `context.term = 2025`, `context.band = elevated`, and `context.salience_version = sal-v4`. The committed `metrics/statpack.md` heading matches that version. I use its bracketed **reached elevated** risk-set rates, never the evaluator's terminal context or the leading terminal rates. The eligible displayed rows are OT2017–OT2024; OT2025 and OT2026 are excluded. Their published rates and weighted resolved denominators are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336, respectively. Thus the pooled baseline is 484.386 / 2,810 = **0.172379359430605**, with `base_rate_basis = risk_set`. The numerator is a grant-equivalent reconstructed from rounded published rates, not an exact grant count. The caption renders 10 of 10 Terms, so there is no omitted-window divergence to flag.

These are calculations from the committed, denial-reweighted live/historical-slice statpack supplied in this checkout, not fresh corpus measurements. I did not query or refresh the corpus and do not assert a newest-pull vintage. Case ground truth is the provisioned October 5, 2026 outcome and snapshot.

This is a **cert** event. No vote accuracy, judgment score, or semantic grades are supplied. Quantitative claims are left for the harness; the court-action forecast document was read only for context and leakage review, not scored. The quality judgment below is confined to `reasoning.md`, independently of exact-match and Brier performance. The short denial supplies no Court explanation, so it does not establish that any hypothesized reason actually motivated the Court.

## Reasoning quality: 0.65

The rationale recognizes the central vehicle problem: a cert-before-judgment petition from an unfinished Fifth Circuit appeal is different from the companion petition following an appellate judgment. It also uses the government's response waiver as a reason not to equate national stakes with likely review. These are relevant, record-based considerations, and the denial forecast is correct.

The stated anchor is materially wrong: **13.5% is the displayed OT2025 reached-elevated rate**, the prediction's own docket Term, not the required pooled prior-Term rate. The correct rendered pool is approximately 17.24%. This is not a salience-version mismatch, so the evaluator still records the supported risk-set baseline and computes skill against it. The error is surfaced in the cell's flags rather than repaired inside the prediction.

The discussion also calls the district-court/Eleventh-Circuit disagreement a developing circuit split, without establishing a conflict between courts of appeals. It does identify the two courts, which makes the limitation visible, but overstates the conflict's procedural maturity. The rationale does not engage the petition's domestic-company exemption, live-controversy discussion, or abeyance pending rulemaking, all relevant to the urgency argument. Its balancing from a purported 13.5% anchor to 15% remains sketchy. The score credits the sound core vehicle analysis but discounts the baseline error, imprecise split characterization, and incomplete treatment of the provided petition context; it does not penalize brevity or grade the separate claims/forecast.

## Leakage assessment

`mode = forward`; `retrieved_outcome_material = false`; `influenced_prediction = not_applicable`; `leakage_suspected = false`.

All 22 logged calls are marked unobserved, with capture coverage 0.0. Their null document dates and digests do not establish that no information returned. The available queries name provisioned pre-decision inputs and the statpack, not this petition's outcome or later docket history; the reasoning does not presuppose the denial. The September 18 activity precedes the October 5 resolution. The own-Term aggregate-anchor mistake is a baseline-selection error, not evidence of retrieving this case's disposition, and does not trigger outcome-leakage exclusion. This assessment rests on query scope and prose with the telemetry limitation disclosed, not on an absence of captured results.
