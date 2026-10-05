# Evaluation: codex-baseline

## Outcome and numerical scores

The authoritative outcome records `denied`, `actual_granted = 0`, resolved October 5, 2026. The provisioned snapshot ends with the same denial. The candidate predicted `denied` with P(any grant) = 0.025. Exact-label correctness is **1**. Brier loss is `(0.025 - 0)^2 = 0.000625`. Skill against the reached-band baseline is `1 - 0.000625 / (0.05120250431778929 - 0)^2 = 0.761604742464263`. A correct denial does not show why the Court denied; the outcome records no explanatory holding.

## Reasoning quality: 0.90

The rationale carefully distinguishes the frozen baseline band from terminal procedural statistics and pools the displayed strictly prior Terms. It treats the alleged circuit disagreement as petitioner's characterization rather than an independently established conflict on identical facts. Its central objections are concrete: the unexplained original-jurisdiction refusal, alternative state-law grounds, uncertain preservation, and the difference between a neighborhood challenger and a permit holder. These points track the petition's account without pretending the unexplained order establishes which ground actually controlled. It also separates a response waiver from an affirmative sign of Court interest, and does not count summer delay as a relist.

The treatment of the proposed clarification remand is balanced: the rationale reports checking a historical authority, acknowledges that a route exists, and explains why its availability does not compel relief in this vehicle. The captured log supports that historical-authority retrieval; I did not independently retrieve or re-adjudicate the authority. The candid acknowledgment of unread supplemental briefing and missing underlying state-court materials appropriately limits confidence. The actual denial agrees with the headline call, but supplies no merits holding and does not validate the proposed explanation.

The principal limitation is numerical: reducing the approximately 5.12% anchor to 2.5% is a reasoned subjective adjustment, not an empirically calibrated mapping of these defects to a probability. The account identifies that uncertainty rather than disguising it. This earns reasoning_quality = 0.90 on analytical soundness, not on having a smaller Brier loss; its Brier is in fact larger than the other two denial forecasts.

## Baseline and scope

This is a **cert-stage** evaluation. The baseline uses this candidate's own frozen `context.band = baseline`, `salience_version = sal-v4`, and `term = 2025`, not the evaluator's decided-docket context. The committed statpack heading matches sal-v4. I pool all eight displayed strictly prior Terms, OT2017–OT2024, using the bracketed reached rates and their denial-reweighted resolved denominators: 4.7%/1643, 4.6%/1524, 4.6%/1399, 4.5%/1739, 5.6%/1500, 5.8%/1192, 5.9%/1312, and 5.7%/1271. The weighted denominator is 11,580 and the weighted rate is approximately 0.05120250431778929. The numerator implied by the rounded rates is 592.925 weighted grant equivalents, not an exact count of observed grants. Both the baseline and derived skill inherit that display-rounding approximation. `base_rate_basis` is `risk_set`. OT2025 and OT2026 are excluded. The caption renders 10 of 10 Terms, so no rendered-window divergence needs a flag.

This uses the committed pack, not a refreshed corpus or a claim about current corpus coverage. Case evidence is the provisioned October 5, 2026 snapshot and outcome; the predictions' frozen snapshots are dated September 16, 2026. I did not query the corpus. One realized denial does not establish comparative calibration or general forecasting performance.

Reasoning quality grades the analytical content of `reasoning.md` only. The forecast document was read for context but not scored. The quantitative claims and their rationale are left to the harness rather than graded as additional accuracy or folded into reasoning quality. No vote accuracy is written: cert votes are unscored regardless of observability. No semantic set is declared for this cert event, so no semantic grades are written. No independent big-case assessment is offered. Harness-owned provenance, context and claim-score fields are left absent.

## Leakage assessment

The log records forward mode and 28 calls on September 16, with capture coverage 0.9285714285714286. Two unobserved web attempts concern the historical Philadelphia Newspapers authority; their null results cannot substantiate the prose's no-usable-content claim. Captured follow-up queries and an opinion-id read concern that authority, not this petition's outcome. The instructions search explicitly excludes the prohibited labeling path; it is not evidence of reading those artifacts. No October 5 disposition surfaces in the query record or reasoning. Influence is not_applicable.

`retrieved_outcome_material = false` records no affirmative evidence of this case's disposition in the staged log or prose; it is not a claim that uncaptured results were empty. `leakage_suspected = false`. The later, decided snapshot available to this evaluator is not treated as the predictor's earlier information set. No leakage or data-quality flag is warranted by the evidence reviewed.
