# Evaluation of `codex-baseline`

## Outcome and Quantitative Scoring
- **Stage**: Cert (`evt-petition-disposition`).
- **Outcome**: Denied on October 19, 2026 (`actual_disposition: "denied"`, `actual_granted: 0`, `distribution_count: 2`, `noted_dissent_from_denial: false`).
- **Prediction**: `predicted_disposition: "denied"`, `probability: 0.16`.
- **Accuracy & Brier**: `correct = 1`, `brier_score = (0.16 - 0)^2 = 0.0256`.
- **Segment Base Rate**: Because the scored prediction carries a frozen `context.band` (`elevated`, `sal-v4`), the segment base rate, basis, and Brier skill score are left null for the harness to stamp (`the stamped segment base rate`).

## Reasoning Quality (`0.90`)
`codex-baseline` delivered a rigorous, well-calibrated, and methodologically disciplined analysis:
1. **Accurate Procedural Reading**: Unlike naive readings of `distribution_count: 2` as a post-conference relist, `codex-baseline` accurately traced the docket timeline—noting that the June 9 distribution for the June 25 conference was superseded on June 12 by the Court's call for a response, and that the September 30 distribution simply set the petition for its first fully briefed conference on October 16, 2026 after the Solicitor General and VirtaMove filed their briefs in opposition and Google filed its reply.
2. **Doctrinal and Vehicle Analysis**: `codex-baseline` carefully separated the two briefs in `brief-in-opposition.txt` (VirtaMove's July brief and the Solicitor General's September brief) and identified the decisive obstacles that led to the October 19 denial: the demanding *Cheney* mandamus standard, the statutory bar in 35 U.S.C. § 314(d) under *Cuozzo* and *Thryv*, the nonprecedential two-page nature of the Federal Circuit order, and the factual dispute over whether the PTO applied a categorical six-year rule or a holistic discretionary assessment to a 14-year-old patent.
3. **Appropriate Calibration**: Starting from the stamped segment base rate, `codex-baseline` balanced the genuine indicators of institutional interest (seven diverse amicus briefs and the Court's June 12 response request after the PTO's initial waiver) against the formidable mandamus/reviewability barriers and the federal government's opposition, arriving at 0.16—and rightly predicting a straight denial after the October 16 conference without further redistribution.

## Leakage Assessment
- **Mode**: `forward` (run on 2026-09-30; event resolved on 2026-10-19).
- **Assessment**: `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`.
- **Evidence**: The case was genuinely open at prediction time. The retrieval log shows 34 calls (capture coverage ~94.3%): local file reads of the provisioned record and statpack, two unobserved web searches for the statutory text of 35 U.S.C. § 314 on `uscode.house.gov`, and CourtListener MCP lookups of *Cuozzo Speed Technologies, LLC v. Lee*, 579 U.S. 261 (2016).
