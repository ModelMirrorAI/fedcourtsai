# Evaluation: codex-baseline

## Outcome and quantitative scores

The cert-stage outcome records `denied` on October 13, 2026, and `actual_granted = 0`. The candidate's disposition matches exactly: `correct = 1`. Its grant probability was 0.025, yielding `(0.025 - 0)^2 = 0.000625`. The outcome supplies no merits rationale; it confirms the label, not the candidate's explanation of why review was unlikely.

The prediction froze the baseline band under sal-v4. The harness supplies the segment base rate, basis, and Brier skill; I leave those fields absent and refer any comparison to the stamped segment base rate. I do not reproduce or independently pool the candidate's historical anchor. Cert votes are not scored, no semantic set applies, and the mechanical claims and forecast document remain outside this assessment.

## Reasoning quality: 0.92

The rationale carefully separates petition advocacy from the lower court's actual reasoning. Petition Part III asserts that no reported decision applies the doctrine in this precise setting, which is not a demonstrated conflict between appellate holdings. Part IV supplies the alternative request for state-law certification. Appendix A, pages 5–7, supports the candidate's account of the panel's contract language, effective-date restriction, and distinction between an existing loss and a preexisting condition. The rationale does not turn its unfavorable vehicle assessment into endorsement of the insurer's merits position.

It also gives the Erie objection genuine, limited weight rather than simply denying that any federal question is presented. Its treatment of the absent opposition brief, the arrival-stage absence of docket signals, and the limitations of aggregate historical context is appropriately cautious. The anchor and downward adjustment are explained rather than merely asserted, although I have not independently reconstructed the historical pack used at prediction time.

The residual limitation is quantitative: the record supports a downward direction more securely than the exact size of the adjustment, and the argument for multistate importance remains largely the petitioner's assertion. Those uncertainties preclude a perfect score but do not undermine the central, balanced analysis. This quality grade concerns the rationale alone, not the successful label, the forecast's timing, any mechanical claim, or the candidate's stakes score.

## Leakage and record limits

Both the frozen context and the captured log identify forward mode, with calls on September 27 before resolution. The log has 26 captured calls and four unobserved general Rule 10 searches/official rules opens. Unobserved means the results were not captured; it does not verify the retrieval note's statement that nothing usable returned. Grading those calls by their queries, however, shows no attempt to retrieve this case's later docket or outcome. The remaining reads concern the supplied materials, aggregate statistics, and output tooling. No disposition is presupposed in the rationale. Outcome material is not evidenced, influence is `not_applicable`, and leakage is not suspected; incomplete capture remains an observation limit, not a defect or affirmative leakage finding.

My independent stakes assessment is 0.20: meaningful private coverage and potential model-law implications, bounded by an individual Iowa dispute without a demonstrated square appellate split. It is not part of the reasoning-quality grade. Case observations are limited to the supplied documents and October 13 snapshot; I made no fresh corpus inquiry.
