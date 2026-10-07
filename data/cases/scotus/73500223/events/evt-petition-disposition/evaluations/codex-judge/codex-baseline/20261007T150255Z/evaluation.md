# Evaluation: codex-baseline

## Outcome and quantitative scores

This is cert-stage. The outcome records `denied` on October 5, 2026 and `actual_granted = 0`, consistent with the denial entry in the provisioned October 5 snapshot. codex-baseline names `denied`, yielding `correct = 1`; its 0.08 grant probability gives `(0.08 - 0)^2 = 0.0064`.

The baseline is keyed to the prediction's frozen `baseline` band, `sal-v4` version and Term 2025. The committed statpack's version matches. Its rendered bracketed reached rates for all strictly-prior Terms are 2017 (4.7%, n=1643), 2018 (4.6%, n=1524), 2019 (4.6%, n=1399), 2020 (4.5%, n=1739), 2021 (5.6%, n=1500), 2022 (5.8%, n=1192), 2023 (5.9%, n=1312), and 2024 (5.7%, n=1271). Their resolved-weighted mean is 0.05120250431778929 over n=11,580, with `base_rate_basis = risk_set`.

Skill is `1 - 0.0064 / 0.05120250431778929^2 = -1.4411674371659498`. Naming denial was correct, but the probability uplift above the baseline costs Brier accuracy on this denial. That is one-event performance, not an aggregate conclusion about the predictor.

This evaluation uses the displayed markdown percentages, which are rounded. The predictor reports a slightly different anchor, 593/11,580 = approximately 0.051208981, from unrounded JSON for the same window. The tiny discrepancy is consistent with printed-percentage rounding, not a different population or timing cut; no deduction is assigned for it. The table states ten of ten Terms displayed, so its eight strictly-prior rows do not omit a hidden older pack window. These are supplied committed historical, denial-reweighted estimates, not a refreshed live-corpus measurement. No live corpus vintage is asserted.

## Reasoning quality: 0.93

The rationale is detailed, balanced and careful about what the available material can support. It distinguishes a first distribution from a completed relist, a filed opposition from a Court-requested response, and the docket-number Term from the expected disposition Term. It chooses the matched risk-set baseline and explicitly avoids turning terminal relist buckets into an incremental hazard. These distinctions directly bear on the probability being forecast.

The case-specific analysis weighs the constitutional reconsideration request and amicus interest against preliminary-injunction posture, undeveloped facts, absence of an established federal split, and the parties' dispute about later precedents preserving PruneYard distinctions. Those issues are apparent in the supplied opposition's introduction and vehicle discussion. The rationale identifies relevant petition and opposition passages, records earlier-precedent verification, and avoids calling preliminary posture an adjudicated jurisdictional bar. It also distinguishes a grant-family probability from the exact complement of denial and does not confuse likely denial with low potential doctrinal stakes.

The remaining limitations prevent a perfect score. The move from roughly 5.1% to 8% remains a subjective adjustment with no estimated likelihood ratio. The candidate expressly lacks the reply and independent appellate-record review, leaving its account of potential answers to the vehicle objections incomplete. These are transparently acknowledged limits, not grounds to infer that the denial proves the legal analysis wrong. The Court's denial gives no reasons and does not establish which predicted screening concern actually mattered.

The rating evaluates only `reasoning.md`; neither the forecast document nor the quantitative claims contribute a second outcome score. The rationale's statement about the historical event schema is not treated as a substantive error merely because the evaluator's current event file now includes stage and moment fields.

## Leakage and scoring scope

The log identifies a September 17 forward run. Its queries concern provisioned inputs, the committed statpack and earlier Supreme Court precedents; the Cedar Point search is bounded before 2022 and the Moody search before 2025. There are 41 calls: 39 captured and two unobserved web rows, giving capture coverage approximately 0.9512. Although the candidate describes the web attempts as returning no usable content, the unobserved markers do not independently establish that; I assess their visible query scopes instead. They seek an earlier authority and its official opinion, not this petition's later disposition. Collapsed `other` call labels are not treated as suspicious by themselves.

Neither the transcript nor the rationale exposes the petition's October 5 denial as already known. The pending September 28 conference chronology is consistent with a genuinely unresolved forward case. I therefore record outcome-material retrieval as false, influence as `not_applicable`, and suspected leakage as false, without treating absent result dates or unstaged disclosures as proof of cleanliness. The evaluator's later snapshot is not substituted for the candidate's historical baseline.

Cert votes are not scored, no semantic set is declared, and mechanical claim scores remain the harness's. No independent big-case score is supplied.
