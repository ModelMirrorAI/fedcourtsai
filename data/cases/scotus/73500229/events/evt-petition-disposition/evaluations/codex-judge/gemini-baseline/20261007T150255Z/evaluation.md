# Evaluation: gemini-baseline

## Outcome and numerical scores

The cert-stage outcome is `denied`, resolved October 5, 2026, with `actual_granted = 0`. gemini-baseline's September 17 prediction also named `denied`, at any-grant probability 0.08. Exact-label correctness is 1 and Brier = `(0.08 - 0)^2 = 0.0064`.

Use the prediction's frozen `baseline` band under `sal-v4`, Term 2025. The committed statpack's matching salience table renders 10 of 10 Terms. All displayed strictly-prior baseline reached rows are pooled: 2024 5.7%/1271; 2023 5.9%/1312; 2022 5.8%/1192; 2021 5.6%/1500; 2020 4.5%/1739; 2019 4.6%/1399; 2018 4.6%/1524; 2017 4.7%/1643 (rate/weighted resolved n). The executed calculation yields 0.05120250431778929 over n = 11,580, with `base_rate_basis = risk_set`. Neither own-Term nor later-Term observations enter, and there is no rendered-window truncation. Rounded table percentages limit precision.

Skill = `1 - 0.0064 / 0.05120250431778929^2 = -1.4411674371659502`. The negative value means this event's probability did worse than the specified constant baseline despite the correct modal label; it says nothing by itself about overall forecast skill. These are the committed statpack figures read October 7, without a fresh corpus query. The candidate's own 5.7% single-Term anchor does not replace the required pooled scoring baseline.

## Reasoning quality: 0.55

Only `reasoning.md` is graded. It identifies a sensible upward signal in the requested response after waivers and a plausible downward consideration in the absence of a clear asserted circuit split. It recognizes uncertainty about the federal statutory issues instead of treating denial as certain. These are relevant cert-selection considerations, and the disposition forecast is consistent with the realized denial.

However, the explanation does not adequately connect those signals to 8%. It takes only OT2024's 5.7% reached figure rather than pooling all displayed eligible Terms. Its generic reference to similar mandate-case denials is not tied to identified cases, and it does not analyze the petition's documented reliance on the unpublished Curtis-controlled affirmance or the threshold vehicle questions that would distinguish this petition. The QPs combine Fourteenth Amendment theories with FDCA/PREP Act predicates; compressing them into statutory preemption alone leaves important legal framing unexplained. Fading pandemic salience is offered as a reason without considering the continuing damages posture in detail.

There is also a concrete sourcing limitation: the rationale says `documents.json` confirmed petition, BIOs, and QPs and that these were reviewed. The provisioned manifest lists only the petition and questions-presented extraction, both fetched July 18, before the August 24 oppositions. The staged log shows petition excerpts and general research, but no identifiable BIO fetch or read. This makes the asserted manifest support incorrect on the available record and the claimed BIO review uncorroborated. Because result bodies are unobserved, I do not infer what the general search actually returned or categorically claim that no relevant material could have been seen. This discrepancy is recorded in the cell's flags. The deduction concerns evidentiary discipline and analytical completeness, not brevity, identity, or the separately scored forecast document.

An unexplained cert denial does not establish the merits of the legal theories, so correctness alone cannot cure these gaps.

## Leakage assessment

The harness marks the prediction forward. Logged calls occurred September 17, before the October 5 outcome, and concern the provisioned September 17 snapshot, petition excerpts, statpack, a general PREP Act corpus query, and a general CourtListener search. No observed query asks for this petition's result, and the rationale does not refer to a known disposition. The assessment is therefore retrieved outcome material false, influence `not_applicable`, and leakage suspected false.

Result capture coverage is 0.0: every marker-bearing result is unobserved. Null dates or digests are not proof of failed or empty retrieval. This is a visibility limitation, not a defect or an independent leakage finding. The source-review discrepancy above does not show that outcome material was retrieved. No retrospective cutoff is imposed on a genuine forward cell.

## Scope

The forecast document was read but not scored. Its relist and writing forecasts and all mechanical claims are excluded from reasoning quality and left for the harness's designated scoring. Cert-stage votes and semantic grades are omitted. No independent big-case assessment or harness-owned stamps are written.
