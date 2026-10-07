# Evaluation: claude-baseline

## Outcome and quantitative score

This is a cert-stage arrival event. The provisioned outcome records a standard plenary grant on October 1, 2026: `actual_disposition = granted`, `actual_granted = 1`. The October 4 snapshot independently contains the October 1 entry, "Petition GRANTED." claude-baseline's August 16 prediction names `granted`, so exact-label correctness is **1**. Its grant-family probability is 0.78; the Brier score is **(0.78 - 1)^2 = 0.0484**. This evaluates the petition's disposition, not the eventual merits judgment.

## Reasoning quality: 0.87

The rationale distinguishes grant-family probability from a plenary grant and distinguishes review of an issue from review on this particular docket. Its reported sister-circuit research supplies a concrete statutory question and competing appellate positions, rather than inferring a conflict from the federal caption alone. The companion-vehicle analysis identifies a material way that a certworthy issue could still yield a hold followed by denial or GVR on this docket. It expressly discloses the absence of the petition text and that its substantive account comes from citing opinions. These are substantive strengths of the analysis, not rewards for the realized grant.

The remaining uncertainty is material: the assumed lead-vehicle share and conditional government-merits probability are judgment calls without an empirical calibration, and the displayed decomposition is closer to 0.76 than the committed 0.78. Its characterization of near-certain issue review is stronger than the staged evidence alone establishes. The captured log supports the occurrence of the cited research, but provides digests and query slices, not the complete opinions needed to independently verify every reported holding. I do not treat the eventual grant as verification of those legal propositions.

Only `reasoning.md` receives this quality grade. The forecast document was read for context; neither its timing forecast nor the quantitative claims receives a separate or implicit grade here. Claim scores remain the harness's. Votes and semantic grades are not scored on this cert cell.

## Baseline refusal

The prediction freezes `band = federal`, `salience_version = sal-v3`, and Term 2026. The committed statpack available to this evaluation labels its segment table **sal-v4**, with 10 of 10 Terms rendered. A sal-v4 rate cannot score a sal-v3 frozen band, even if the federal column appears numerically similar. Accordingly `segment_base_rate` and `brier_skill_score` are omitted and `base_rate_basis` is null. I neither substitute the evaluator's terminal context nor relabel the frozen band as a terminal basis. This mismatch is recorded in the cell's `flags.json`; it is not a reasoning penalty for the candidate's use of its then-available pack. The candidate's reported historical anchor is discussed as its rationale, not adopted as a validated evaluation baseline.

## Leakage assessment

The harness log records forward mode and 29 calls, all marked captured. Calls dated August 16 read the provisioned August 16 snapshot, search opinions citing this case, inspect a companion docket, and consult corpus priors. Legible retrieved dates are before this petition's October 1 resolution. The companion's pending status is reported in the rationale; the log confirms a companion-docket query rather than a query for this petition's disposing order. No staged reasoning reads the October grant as already known. The evaluation's October 4 snapshot is not the candidate's original baseline and is not used to infer what the candidate saw.

Thus `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is an assessment of the available transcript and prose, not an assertion that result digests expose every returned word. No external retrieval was needed for this evaluation.
