# Evaluation: claude-baseline, scotus/9026000359, evt-petition-disposition

**Cell:** cert stage, forward, distribution moment. **Outcome:** `denied` (2026-11-09), one distribution, no CVSG, no noted dissent.

**Scores.** Predicted `denied` with P(grant) = 0.005, so `correct` = 1 and Brier = 0.000025. The segment base rate, basis and skill are stamped by the harness (frozen band `baseline`, sal-v4). Compare against the stamped segment base rate. Vote accuracy does not apply on a cert cell.

**Reasoning quality: 0.85.** The analysis is accurate and grounded in the record. It anchors on the band's risk-set (reached) rate and treats it as a ceiling. It then adjusts down for the right reasons:
- the respondents waived a response and the Court has not called for one;
- the questions presented ask for error correction, with no pleaded split;
- the case reached the Court on summary judgment with Monell and qualified-immunity grounds.

Its vehicle observations check out against the record. The petition invokes 28 U.S.C. §1257(a) for a federal court of appeals judgment, and it leans on *Williamson County*. It correctly calls the opinion below published (the appendix heading reads "RECOMMENDED FOR PUBLICATION") and names the panel correctly. It is candid that it read the appendix only in part. Small deductions: a 0.5% figure carries very little support beyond judgment, and the reading of the appendix was partial.

## Predicted reasoning

**Grade: 0.6.** The central claims are:
- denial at the November 6 conference without a call for a response;
- no further distribution;
- no CVSG;
- no separate writing.

All four were borne out by the docket and outcome.json. The document is specific about timing and about the paths it rules out, with about 5% on a call for a response. But a quick denial of a paid, waived, error-correction petition is what almost any competent reader would have forecast. Under the rubric's specificity rule that sits a little above the generic middle, not at the top. The content conditional on a grant (a reframed Monell question, a 20% summary route) is unresolved and neither credited nor penalized.

## Leakage

The cell is forward, with `cutoff` null and a 2026-10-15 snapshot. The log shows only provisioned inputs, the statpack and schemas. Nothing is dated on or after the resolution, and nothing touches data/qp-topics. `not_applicable`, not suspected.

## Big case

0.07. The case is a local, fact-bound permitting dispute, denied at its first conference.
