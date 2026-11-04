# Evaluation: codex-baseline

**Cell:** scotus/9526000602 (26A602, *Nichloson v. U.S. Bank National Association*), `evt-motion-disposition`. **Stage: interim** (a stay application). **Outcome:** `denied`, `interim_reading: denied`, `interim_granted = 0`. Docket: "Application (26A602) denied by Justice Thomas" (Nov 3 2026), with no response requested, no referral and no amicus briefs.

**Scoring.** On an interim cell with the finer reading, `correct` is a granted/ungranted side match and `brier_score = probability^2` against `interim_granted = 0`. The segment baseline and skill are the harness's: `stamp-cell` pools the interim substantive slice over prior application-Terms. I left `segment_base_rate`, `brier_skill_score` and `base_rate_basis` null and quote no rate of my own. The prediction carries no cert band, so no band flag applies. `claim_scores` (interim set) is the harness's. No vote accuracy is scored on an interim cell, and no semantic set is declared.

**Record note.** The application text staged for me is OCR'd (`ocr_derived: true`). The predictors saw a blank `application.txt` (`empty_text: true`). It is a template-like pro se request to Justice Thomas, as Circuit Justice, for a temporary stay of execution of a writ of possession on a Miami property, pending the Eleventh Circuit's ruling on a stay motion in No. 26-13319. The district court had denied a stay. I graded each candidate against what it could have known.

## Score
- Predicted `denied`, P(grant) = 0.04, so `correct` = 1 and `brier_score` = 0.0016.

## Reasoning quality: 0.65
The reasoning is careful and disciplined:
- The pool is computed correctly (160/1,366 = 11.71%), with unparsed counts noted.
- It recognizes that the cert-petition query rows were not interim analogues.
- It flags the docketing-date anomaly openly.
- It is explicit about what the blank application left unknowable.

It is also the least analytically informative of the three. It declined to infer a foreclosure posture from a bank respondent and a self-represented applicant, which is a reasonable, low-cost inference. It also did not look for the lower-court docket, which was readily available. As a result it applied only a generic downward adjustment and kept 4% for unknowns. The 4% is defensible given an unreadable filing, but it is less well-grounded than it could have been. Its non-zero increments of 12% for a response request and 16% for a referral are high for this population, but those are claim-scored by the harness and not graded here.

## Predicted reasoning: 0.60
I treated these as central: (1) denial by a short Thomas order with no writing; (2) no response, referral or amicus; (3) disposition around early to mid-November; (4) the denial announces no rule.

All four were borne out. The denial came Nov 3, fourteen days after submission. The document is deliberately generic: it commits to little beyond the default path, and it declines to forecast any ground. Under the specificity rule that places it in the middle of the scale.

## Leakage
The cell is forward and was predicted 2026-10-31. The log shows provisioned reads, statpack and statpack.json counts, and one corpus query for cert petitions; its captured result is dated 2026-04-29 and concerns other cases. It also shows three uncaptured web calls. Graded on their queries, they targeted the Supreme Court Rules PDF and a generic Rule 23 search, not this case. Nothing touches data/qp-topics. Graded `not_applicable`, not suspected.

## Big case
My own read is 0.02. The candidate left its own score null, which is its choice and is not graded here.
