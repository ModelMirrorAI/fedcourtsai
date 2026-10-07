# Evaluation: codex-baseline

## Outcome and quantitative scores

The cert petition was denied on October 5, 2026, according to `outcome.json`;
`actual_granted` is 0. The candidate's `denied` label is correct. Its grant
probability of 0.10 yields Brier loss `0.10^2 = 0.01`. The unexplained denial
does not verify any particular account of why review was refused.

The frozen prediction context is Term 2025, `elevated`, `sal-v4`, matching the
committed statpack's salience table. Its caption renders all 10 of 10 Terms.
Using only strictly-prior 2017-2024 bracketed reached figures, the ascending-Term
rate/weight pairs are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397,
20.5%/342, 19.0%/300, 17.5%/354, and 17.9%/336. Their weighted numerator is
484.386 and denominator 2,810, so the `risk_set` baseline is
0.172379359430605. Terms 2025-2026 do not enter. The estimates describe the
denial-reweighted live/historical slice, and published rounding prevents an
unrounded-count reconstruction. This is the committed reference pack, not a
fresh corpus read; the inspected table supplies no build timestamp. Skill is
`1 - 0.01 / baseline^2 = 0.6634655912806073`. Neither the terminal-band
figures nor the evaluator's decided-docket context enters the calculation.

## Reasoning quality: 0.92

The rationale is unusually clear about which facts are in the baseline and
which documents were unavailable. It correctly uses the strictly-prior
risk-set anchor and distinguishes a response-request redistribution from
substantive repeated conference consideration without changing the frozen
band. Its split analysis separates White's discretionary result from the
broader proposed categorical rule and allows for a narrower, genuine tension
in Gilliam rather than adopting every claim in the BIO as established fact.
The provisioned appellate appendix and BIO support the core distinctions.

The discussion also treats preservation as respondent's contention, not a
judicial finding; accounts for the remand separating past and future damages;
and distinguishes original monetary awards from remaining exposure. Its
downward adjustment to 10% balances real attention signals against split and
vehicle weaknesses. The candidate acknowledges that this is not a fitted
likelihood ratio and that the reply, amicus text, and independently checked
Third Circuit authority are missing. Those are appropriately bounded
limitations. The precise 10% remains a subjective calibration, so the grade
is high but not perfect. This assessment concerns the rationale's evidentiary
discipline, not the forecast document or auxiliary claim accuracy.

## Leakage assessment

The log's forward calls occur on September 17, before the October 5 denial.
They concern staged case materials, the statpack, and earlier general
precedents. No visible query or rationale indicates this petition's outcome
was already known. The find-for-instructions command explicitly excludes the
labeling-artifact path; it is not a read of that material.

Capture coverage is 27/28. The web query naming White v. Chafin is unobserved,
so the candidate's report of no usable web results cannot establish what was
returned. The query concerns earlier authority rather than this petition's
disposition. Other lookup rows have captured-result digests, although their
null extracted dates are not independent proof of publication dates. The
retrieval note identifies the mistaken citation lookup as discarded. Together
with the pre-resolution timing and outcome-free rationale, this supports
`retrieved_outcome_material = false`, `not_applicable`, and no leakage
exclusion, without pretending to inspect uncaptured result bodies.

The forecast document was read only for context. Claim scores and provenance
stamps remain the harness's. This cert cell receives neither a vote score nor
semantic grades. The optional independent big-case assessment is omitted.
