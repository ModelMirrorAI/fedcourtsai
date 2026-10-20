# Evaluation — codex-baseline

## Cell

Cert-stage, forward cell: *Allen v. Stein* (scotus/9026000114), `evt-petition-disposition`. Outcome: **denied** on 2026-10-19 (`actual_granted` 0), two distributions, no CVSG, no noted dissent from denial. The prediction froze `context.band` = `elevated` under `sal-v4` (Term 2026), so the segment base rate, `base_rate_basis` and Brier skill are the harness's risk-set stamp; I left them null and quote no rate of my own. Where comparison matters, read it against the stamped segment base rate. `correct` and `brier_score` below are my elicited reads, which the stamp recomputes and compares.

No semantic block applies (cert stage); votes are not scored at cert.

## Scores

- Predicted `denied`, P(grant) = 0.16 → **correct = 1**, **Brier = 0.0256**.

## Reasoning quality: 0.80

Careful and well-disciplined. It anchors on the pooled elevated-band rate (16.9%), uses the relist and CVSG cuts only as shape checks, and notes that the early first conference makes administrative redistribution a plausible explanation. It identifies the central weakness the denial bears out: the panel purported to apply *Swint*'s categories (appendix 21a–25a), so the case presents disputed application rather than a clean split on the legal test. It also covers the Rule 60 reopening and prior-trip vehicle problems and the contested waiver that undercuts summary reversal. It checked *Swint*'s reservation of the scope question directly. Against that, having found substantial vehicle and conflict problems, it ends essentially at the anchor (0.16), so its own analysis was not fully reflected in the number. Its 0.40 summary-route figure also looks high given the contested waiver it describes.

## Leakage

Forward; `not_applicable`. Two web-search rows are unobserved, so I graded them on their queries: Supreme Court Rules / Rule 10 and the official rules PDF, neither about this case. The candidate reports that both returned nothing usable. CourtListener lookups were for *Swint* (1995). No query reached this petition or its subsequent history.
