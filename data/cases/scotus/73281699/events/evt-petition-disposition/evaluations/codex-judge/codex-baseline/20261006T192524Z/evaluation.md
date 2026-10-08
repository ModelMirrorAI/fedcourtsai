# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage evaluation. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. codex-baseline's September 17 prediction names `denied`, so exact-label correctness is **1**. Its grant probability is 0.25; the Brier score is `(0.25 - 0)^2 = 0.0625`.

The baseline uses the prediction's frozen Term 2025, band `elevated`, and version `sal-v4`, not the evaluation cell's terminal context. The committed statpack heading matches that version. Pooling the bracketed reached rates over every rendered strictly-prior Term gives these rate/weighted-denominator pairs: 2024: 17.9%/336; 2023: 17.5%/354; 2022: 19.0%/300; 2021: 20.5%/342; 2020: 16.1%/397; 2019: 13.8%/334; 2018: 15.9%/347; 2017: 17.5%/400. Their denominator is 2,810 and the resolved-weighted rate is **0.17237935943060498**, on the `risk_set` basis. Terms 2025 and 2026 are excluded. The caption renders 10 of 10 available Terms, so no available table rows are hidden by a shorter rendering window. These are rounded, denial-reweighted published estimates, not reconstructed exact grant counts or a newly refreshed corpus measurement.

Skill is `1 - 0.0625 / 0.17237935943060498^2 = -1.1033400544962046`. The modal label was right, but its upward grant-probability adjustment performed worse than this baseline on the realized denial. This is a single-event comparison, not evidence of aggregate calibration.

## Reasoning quality: 0.90

The score grades only `reasoning.md`. Its principal strengths are accurate conditioning on the frozen risk set, explicit recognition that the two distributions need not represent a substantive relist, and balanced treatment of the alleged standards conflict and the vehicle objections. It distinguishes party advocacy from independently checked authority, explains how Jenevein could support both a conflict and a judicial-prestige objection, and does not convert the opposition's earlier-panel argument into an uncontested holding. It also treats the alternative strict-scrutiny ruling and separate pension proceeding as vehicle considerations rather than established jurisdictional defects. The supplied opposition's discussion of Scott, Jenevein and the judicial robe supports the description of the competing positions.

The analysis discloses the petition appendix truncation, source-date uncertainty and remaining reliance on advocacy. The retrieved reply is described as advocacy rather than judicial fact. Those distinctions make the reasoning auditable without treating the unobserved web results as independently visible to this evaluator.

The main limitation is numerical: the move from about 17.2% to 25% is expressly judgmental, without an estimated likelihood adjustment. Comparator coverage also remains incomplete. The eventual denial does not establish that the vehicle concerns actually motivated the Court, nor does it resolve the constitutional standard; I do not grade the substantive arguments as proved merely because denial occurred.

## Leakage and scope

The harness log records `forward`, 30 calls, and 90% result-capture coverage. All prediction activity precedes the supplied October 5 resolution. The unobserved web queries concern a 2007 comparator and the identified August 3 reply filing. I assess those calls from their queries and the candidate's disclosed use, not from their null result dates. There is no affirmative evidence that this case's outcome surfaced in the log or reasoning. Forward influence is therefore `not_applicable`, and leakage is not suspected.

The forecast document was read for context but not scored. Mechanical claims remain for the harness. Cert votes are not scored, and no semantic-grade block applies. No independent big-case assessment is supplied.
