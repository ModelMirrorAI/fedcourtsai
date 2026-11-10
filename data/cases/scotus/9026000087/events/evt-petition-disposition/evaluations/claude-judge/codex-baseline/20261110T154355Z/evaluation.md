# Evaluation — codex-baseline

**Cell:** scotus/9026000087 (Stevens-Reynolds v. Wilshire Insurance Co., No. 26-87), `evt-petition-disposition`, stage `cert`, forward. **Outcome:** denied on 2026-11-09 after one distribution (conference of 11/6/2026), no CVSG, no noted dissent. The segment base rate, its basis and the Brier skill score are the harness's stamp; I write none of them and quote no rate of my own.

## Score
- Predicted `denied`, P(grant) = 0.008 → **correct = 1**, **Brier = 0.000064**.

## Reasoning quality — 0.85
This is the most record-grounded analysis of the three. It anchors on the sal-v4 baseline reached rate over Terms 2017–2025 and correctly declines to substitute the terminal relist and CVSG buckets. It then adjusts down on specific, cited grounds:
- The petition and BIO pages show a contested split.
- Appendix C shows the unpublished CA5 opinion reciting the Geiserman factors and a prejudice finding, which undercuts the premise of QP 1.
- The BIO raises a preservation objection.
- The order of the summary-judgment and exclusion rulings is disputed.
- Deciding the compliance question would take record-heavy work.

It is careful about what it can and cannot establish, and it rests the adjustment on vehicle problems rather than on pro se status alone. One small deduction: it is long and repetitive in places.

## Predicted reasoning — 0.70
Central claims: denial in the orders after the 11/6 conference with no separate writing; zero additional distributions; no CVSG; vehicle problems outweighing the claimed conflict. All four were borne out, and the last is consistent with an unexplained denial. The conditional content (narrowed QP 1, 85% plenary review) was never tested. The document is specific and correct, but its claims are largely the default path for this posture, so it does not reach the top anchor.

## Leakage
Forward cell; the snapshot is dated 2026-10-12. The log has one CourtListener opinion search for a cited circuit precedent, which returned zero results. It also has web lookups for the general Supreme Court Rules, with results unobserved; the queries are not about this case. No query targets this docket or its outcome, and there are no qp-topics reads. The candidate disclosed all of this in its retrieval.md. Grade: `not_applicable`, not suspected.
