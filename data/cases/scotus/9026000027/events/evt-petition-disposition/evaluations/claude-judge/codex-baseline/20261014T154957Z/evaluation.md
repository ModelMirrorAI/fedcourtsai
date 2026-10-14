# codex-baseline — scotus/9026000027, evt-petition-disposition

**Prediction:** denied, P(grant) = 0.01. **Correct:** yes. **Brier:** 0.0001.

## Cell

Cert stage (`stage: cert`, distribution moment), forward mode. Outcome: **denied** on 2026-10-13 (`actual_granted` 0), one distribution, no CVSG, no noted dissent. The prediction froze `context.band` = `baseline` under `sal-v4` (Term 2026), so the segment base rate, `base_rate_basis` and Brier skill are the harness's to stamp; I left them null and refer only to "the stamped segment base rate". `correct` and `brier_score` are written as my independent read; the stamp recomputes both. No votes are scored on a cert cell, no semantic set is declared, and `claim_scores` is the harness's.

## Leakage

Forward cell made 2026-10-04, before the October 9 conference and the October 13 order. I checked the log for this case's disposition surfacing as already decided and found none: no retrieved document dated on or after resolution, no query for the petition's disposition, no read inside `data/qp-topics/`. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

Log detail: general Supreme Court Rules lookups (web search / fetch of the Rules PDF, all failed or uncaptured) — general law, not case material. Its `find` excluded `data/qp-topics` via `-not -path`, which opens nothing there. No case-specific external retrieval.

## Reasoning quality: 0.85

Thorough and well-disciplined. It anchors on the sal-v4 baseline reached-band rate pooled over strictly prior Terms (638/12,720 ≈ 5.02%), explains why terminal relist/CVSG cuts are not substituted for the forward anchor, and then reduces on three record-grounded factors: an unpublished, expressly narrow Fifth Circuit decision on Louisiana's two-contract defense; no demonstrated conflict (the Virginia district-court example is distinguished); and — correctly identified as the strongest negative — the FECA and Supremacy Clause theories were first raised on reconsideration and on appeal. It fairly states the strongest affirmative case (the federal-inspector question's potential reach) and attributes contested factual accounts to the briefs rather than adopting them. Its 1% leaves somewhat more room for that federal question than the preservation problem warranted, which is the main reason the score is not higher; the analysis itself is careful and calibrated, and the outcome bore it out.
