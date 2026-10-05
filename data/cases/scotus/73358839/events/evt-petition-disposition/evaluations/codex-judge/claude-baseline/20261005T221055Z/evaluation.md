# Evaluation: claude-baseline

Case: `scotus/73358839`; event: `evt-petition-disposition`; evaluator: `codex-judge`; evaluation run: `20261005T221055Z`. Scored blinded prediction run: `20260918T195102Z`.

## Observed outcome and numerical scores

The provisioned `outcome.json` records **denied**, `actual_granted = 0`, resolved **October 5, 2026**. The provisioned snapshot has an October 5 entry reading "Petition DENIED." The candidate predicted **denied** with grant probability **0.08**. Exact-label correctness is **1**; Brier loss is `(0.08 - 0)^2 = 0.0064`. Skill against the shared prior-Term baseline is `1 - 0.0064 / (0.172379359430605 - 0)^2 = 0.784617978419589`. This is a per-cell comparison, not an aggregate performance claim.

## Baseline and scoring scope

The scored prediction freezes `context.term = 2025`, `context.band = elevated`, and `context.salience_version = sal-v4`. The committed `metrics/statpack.md` heading matches that version. I use its bracketed **reached elevated** risk-set rates, never the evaluator's terminal context or the leading terminal rates. The eligible displayed rows are OT2017–OT2024; OT2025 and OT2026 are excluded. Their published rates and weighted resolved denominators are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336, respectively. Thus the pooled baseline is 484.386 / 2,810 = **0.172379359430605**, with `base_rate_basis = risk_set`. The numerator is a grant-equivalent reconstructed from rounded published rates, not an exact grant count. The caption renders 10 of 10 Terms, so there is no omitted-window divergence to flag.

These are calculations from the committed, denial-reweighted live/historical-slice statpack supplied in this checkout, not fresh corpus measurements. I did not query or refresh the corpus and do not assert a newest-pull vintage. Case ground truth is the provisioned October 5, 2026 outcome and snapshot.

This is a **cert** event. No vote accuracy, judgment score, or semantic grades are supplied. Quantitative claims are left for the harness; the court-action forecast document was read only for context and leakage review, not scored. The quality judgment below is confined to `reasoning.md`, independently of exact-match and Brier performance. The short denial supplies no Court explanation, so it does not establish that any hypothesized reason actually motivated the Court.

## Reasoning quality: 0.84

The rationale correctly centers the cert-before-judgment posture, the unfinished appeal, the response waiver, and the companion-petition route rather than treating constitutional importance as sufficient. It distinguishes the pre-conference reschedule from a true relist and uses the correct prior-Term risk-set anchor. The provisioned petition supports the procedural and companion framework. The explicit decomposition into a roughly 15% companion-grant probability times a roughly 50% conditional probability of also taking this case, plus a small independent route, makes the final 8% judgment intelligible, while remaining subjective rather than empirically calibrated.

The largest downward adjustment depends on the candidate's reported August 2026 final rule and its account of the government's companion opposition. The log supports that companion and regulatory retrieval occurred before resolution, but supplies result digests rather than the full external texts. I therefore treat those substantive details as attributed retrieval reports, not independently verified facts. The candidate candidly states that it did not read the opposition or reply themselves and instead relied on secondary reporting and docket metadata. It acknowledges voluntary cessation and the risk that its description of the government's position is incomplete. That disclosure strengthens the analysis, but it cannot eliminate uncertainty in the premise driving most of the probability reduction.

The language about an exemption being permanent and the mandate no longer applying to every petitioner is more categorical than the presented source verification supports, especially alongside the acknowledged continuing statutory challenge. The rationale is otherwise coherent and appropriately distinguishes practical urgency from the underlying constitutional question. A high but submaximal quality score reflects that strong vehicle analysis and transparent conditional reasoning, tempered by source dependence and categorical phrasing. The eventual denial does not verify the candidate's account of the Court's reasons.

## Leakage assessment

`mode = forward`; `retrieved_outcome_material = false`; `influenced_prediction = not_applicable`; `leakage_suspected = false`.

The September 18 log contains 32 calls, all marked captured. It includes CourtListener queries for the companion and pending Fifth Circuit appeal, a companion open-events query, an unrelated recent-grants corpus query, and web retrieval about the companion briefing and regulation. The recorded non-null document dates are December 9, 2024 and April 21, 2026, not the October 5, 2026 disposition. The prose describes August and September developments and both petitions as pending. The log also shows a read of a prior August 20 prediction; it is not a disposition record, and there is no evidence that it exposed an outcome. No forbidden labeling-artifact read appears.

Companion-case developments and regulatory context were permitted forward signals while this petition remained unresolved. I do not mistake the evaluator's October 5 snapshot for the predictor's September 18 information set or treat null extracted dates as proof that every source was undated. The available queries, timestamps, and reasoning show no already-decided outcome of this petition and no forward mis-provisioning.
