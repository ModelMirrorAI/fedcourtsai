# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage petition disposition. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. claude-baseline predicted `denied` with P(any grant) = 0.13, so `correct = 1` and the Brier score is `(0.13 - 0)^2 = 0.0169`.

The prediction itself freezes Term 2025, band `elevated`, and version `sal-v4`; the committed statpack's band-table heading matches that version. I use its bracketed reached rates, not terminal rates or the evaluator's decided-docket context. For Terms 2024 through 2017, the displayed rate/weighted-denominator pairs are 17.9%/336, 17.5%/354, 19.0%/300, 20.5%/342, 16.1%/397, 13.8%/334, 15.9%/347, and 17.5%/400. Their resolved-weighted pool is 484.386 / 2,810 = 0.172379359430605. Terms 2025 and 2026 are excluded. The caption renders all ten available Terms, so there is no omitted-window discrepancy.

This is a denial-reweighted historical-slice risk-set estimate from the committed table, not a fresh remote-corpus measurement. I made no live corpus query and do not assert remote corpus freshness. The fractional numerator is reconstructed from displayed, rounded percentages, not an exact count of grants. Skill against this baseline is `1 - 0.0169 / 0.172379359430605^2 = 0.43125684926422635`. The tiny rounding difference from an unrounded companion rate is not a change of population or window.

## Reasoning quality: 0.86

The rationale is substantive and balanced. It anchors on the compatible prior-Term band, addresses the response request without heavily double-counting it, and explains why the alleged split may be an application disagreement rather than a categorical conflict. It identifies the pleading-stage remand, remaining factual questions, lack of cert-stage amici, and the difference between two distribution entries and repeated consideration of a fully briefed petition. The provisioned opposition's printed pages 11–15 provide concrete quotations supporting the course-of-dealing distinction; its printed page 7 and footnote describe continuing district-court discovery. These are meaningful reasons for a below-band forecast, not hindsight explanations constructed from denial.

The principal weaknesses are inferential overconfidence and incomplete independent verification. The assertion that an invited Solicitor General would very likely recommend denial goes beyond what an earlier appellate merits position establishes. The rationale also characterizes the conflict as collapsing, while acknowledging that it relied on the parties' descriptions rather than independently reading the comparator opinions. These limitations warrant a deduction despite a well-supported overall analysis. The exact four-percentage-point adjustment remains judgmental, not estimated from a fitted model.

The recorded denial supplies the scored label, not the Court's reasons for denying. I do not treat it as proof that any particular vehicle or doctrinal objection motivated the Court. This grade concerns `reasoning.md` alone; the forecast document and structured quantitative claims were read for context but are not graded here.

## Leakage and scoring scope

The harness log records `forward` mode and 28 calls, all captured, on September 18, 2026. The petition was unresolved relative to the supplied October 5 resolution. Case-caption and docket searches were legitimate forward retrieval; the rationale describes a forthcoming conference rather than an already-decided petition. The log's dated docket material is May 1, 2026, and the self-report identifies the government brief as a 2024 appellate filing. No evidence shows this petition's disposing order or outcome being retrieved. Accordingly, influence is `not_applicable` and leakage is not suspected. This finding rests on chronology, queries, and prose together, not merely on null retrieved-document dates.

Vote accuracy is omitted because this is a cert event. No semantic set is graded, and mechanical claim scores and provenance stamps are left to the harness. No independent big-case score is supplied.
