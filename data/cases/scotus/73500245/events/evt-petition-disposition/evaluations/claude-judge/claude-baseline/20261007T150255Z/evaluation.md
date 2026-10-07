# Evaluation — claude-baseline, scotus/73500245, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition in *Blevins v. Alabama State Bar*, No. 25-1344, was distributed once (July 8, 2026, for the September 28, 2026 conference) and **denied on October 5, 2026** without a noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1).

- `predicted_disposition` denied vs actual denied → **correct = 1**.
- `probability` 0.008 → **brier_score = 0.000064**.
- Base rate: the prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`; the statpack's "Segment base rate by salience band (sal-v4)" heading matches, so the basis is **risk_set**. Pooling the bracketed `reached` figure, resolved-weighted, over every rendered Term strictly before this case's Term 2025 (OT2017–OT2024; the table renders 10 of 10 Terms) gives 593 / 11,580 = **0.0512**. The in-code ten-Term lookback would reach OT2015, but the pack holds nothing before OT2017, so the windows coincide.
- `brier_skill_score` = 1 − 0.000064 / (0.0512 − 0)² = **0.976**.

## Reasoning quality: 0.88

This is the strongest analysis of the three. It anchors on the correct pooled risk-set rate (593/11,580 ≈ 5.1%) and says plainly that this is the yardstick skill is scored against. It then does the one thing the other candidates did not: it read the Alabama Supreme Court's opinion below (CourtListener cluster 10761703) and drew the right conclusions from it. I checked the candidate's three claims about that opinion against the text and each holds: the court held § 34-3-62 inapplicable because the Bar prosecuted Rule 1.4 (communication) and Rule 1.5 (fees) violations rather than wrongful retention of funds; it treated the reliance argument purely as a *Brooks* question and distinguished *Brooks* because Blevins relied on no caselaw and had not actually invoked the statute at the time; the opinion contains no Fourteenth Amendment fair-notice analysis as such (its only federal constitutional discussion is a class-of-one equal-protection claim about the sanction); and five of the seven participating justices concurred only in the result, with two recused. From this the candidate correctly identifies the two decisive vehicle problems — preservation of the federal question is doubtful, and the alternative state-law holding means a favorable *Marks* ruling would not necessarily disturb the discipline — and correctly characterizes *Marks*/*Bouie* as a doctrine about unforeseeable judicial enlargement of criminal statutes with no support for extension to a first-time civil construction where no actual reliance was found.

The adjustments are each named and weighted, and the candidate reads the relist-count cut "for shape only" because it describes terminal states. The originating-court figure it cites (Supreme Court of Alabama: 29 resolved, 28 denied, 1 granted) matches `metrics/statpack.json`, and its stated range for the baseline terminal rate (0.6%–1.8%) matches the rendered table. The "Uncertainty and where to discount me" section is honest about the limits of a qualitative adjustment and about which retrievals did not shape the number.

Minor deductions: the stated cert-order share of the grant family ("roughly 37%–59%") is slightly off the statpack's own caption ("30-59%"), a cosmetic slip in a claim that is not mine to score. The relist-increment reasoning leans on a reached-minus-terminal gap as a proxy for leaving the band, which conflates band exit with a second distribution. Neither affects the soundness of the headline analysis.

## Leakage

Mode `forward`. The prediction was written September 17, 2026, before the first conference (September 28) and the denial (October 5), so no outcome existed to leak. The log (31 calls, capture coverage 1.0) shows the external calls the candidate's `retrieval.md` lists and no others: one corpus query for recent scotus denials (returned five other cases), a CourtListener docket search for 25-1344 (0 results), an opinion search returning the decision below (`retrieved_doc_date` 2025-12-19), a docket search for the related M.D. Ala. § 1983 suit (2026-03-01), and a fetch of the opinion below. Every dated retrieval predates the event's resolution and concerns the lower-court record or a related case — legitimate forward signal. No `data/qp-topics/` read. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false.

## Big case

My independent read is 0.04: one attorney's 180-day suspension, a state-law-framed QP with a thin federal hook, no split, no amici, waived response, routine first-list denial. The candidate's `big_case_score` was visible in the staged `prediction.json` I read for the context block, so strict pre-exposure independence could not be kept; the read rests on the record and the outcome.

## Not graded here

The claims block and `predicted_reasoning.md` are harness-scored or unscored by contract. No semantic set is declared on a cert cell, so no `semantic_grades` block is written. `vote_accuracy` is omitted on a cert cell.
