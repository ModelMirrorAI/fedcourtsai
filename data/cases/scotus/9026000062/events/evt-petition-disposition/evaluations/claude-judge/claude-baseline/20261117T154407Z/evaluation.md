# Evaluation — claude-baseline

**Cell:** scotus/9026000062, `evt-petition-disposition` (cert stage, *Custodia Bank, Inc. v. Federal Reserve Board of Governors*, No. 26-62). Outcome: **denied** on 2026-11-16 after a single distribution, no CVSG, no noted dissent.

## Scores
- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.08 − 0)² = 0.0064.
- Base rate, skill and claim scores are the harness's; I wrote none. No votes are scored on a cert cell.

## Reasoning quality — 0.80
The rationale starts from the frozen baseline-band anchor and moves modestly up to 0.08, and every factor it names checks out against the staged record: three amicus briefs, two briefs in opposition (one by the Solicitor General for the Board), a conceded absence of a circuit split with the Second Circuit agreeing, the waived Appointments Clause theory the petition does not challenge, and the pending Payment Accounts rulemaking as a vehicle problem. It correctly weighted the downward factors (no split, SG opposition) as stronger than the upward ones (elite counsel, the Tymkovich dissents, amicus support), and treated the confounded amicus bucket as directional only. The denial at first conference is what that analysis predicted. Deductions: it is brief, it admits it did not read the appendix in full and relied on the briefs' excerpts of the decision below, and the 22% relist figure is asserted more than derived.

## Predicted reasoning — 0.70
Central claims: denial at the 11/13 conference or after at most one relist; no further relist; no CVSG; no separate writing. All four are borne out by the outcome and docket. The document is clear and committed, but each call was the favoured side of a lopsided prior, and the timing claim left room for a relist, so it does not reach the top of the scale. Conditional content (question taken, plenary route, likely author of a writing) never came into play and earned neither credit nor penalty.

## Leakage
Forward, `not_applicable`. The prediction predates the disposition by two weeks; the fully captured log shows provisioned files, the statpack and two generic corpus queries only. Nothing outcome-revealing was retrieved.

## Big case — 0.50
Sector-important statutory question about master-account access, with no split and a quiet denial.
